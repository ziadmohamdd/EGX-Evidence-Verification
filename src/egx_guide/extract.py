"""Turn read pages into evidence items.

A model proposes figures from each page (label, number as printed, period,
unit line). Plain code then decides whether each figure can be trusted:

1. the printed number is found in the page text (grounding),
2. it parses without doubt (digits, sign, separators),
3. the unit/scale is clear and consistent,
4. the period is stated,
5. the page was not read through a right-to-left text layer, where columns
   (and so periods) can be swapped.

A figure that fails any check is kept as an Ambiguous Financial Figure with
the reason, never silently dropped or guessed.

Usage:
    python -m egx_guide.extract --pdf reports/COMI_FY2024.pdf --company COMI \
        --pages 3-6 --provider google --model <model> --out data/evidence
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from .documents import DocumentRecord, PageRecord, parse_pages, read_pdf
from .llm import Caller
from .models import EvidenceItem, EvidenceStatus
from .numbers import contains_number, detect_scale, figure_kind, normalize, parse_amount


class ExtractedFigure(BaseModel):
    label: str = Field(description="Line item name as printed, e.g. 'صافي أرباح الفترة' or 'Net profit for the year'")
    printed_value: str = Field(description="The number exactly as printed, e.g. '(1,234)' or '٢٬٥٠٠'. Never reformat or compute.")
    row_text: str = Field(description="The whole printed row or line containing the number")
    period: str | None = Field(default=None, description="Period of this column as printed, e.g. '31/12/2024' or 'السنة المنتهية في 2024'")
    currency: str | None = Field(default=None, description="Currency if printed, e.g. 'EGP' or 'جنيه مصري'")
    basis: str | None = Field(default=None, description="'consolidated', 'separate' or None if not stated")
    uncertain: bool = Field(default=False, description="True if any digit, sign, column or period is unclear")
    note: str | None = None


class PageFigures(BaseModel):
    statement: str | None = Field(default=None, description="Statement or table title, e.g. 'Consolidated income statement'")
    unit_line: str | None = Field(default=None, description="Unit line exactly as printed, e.g. 'EGP thousands' or 'بالألف جنيه'")
    figures: list[ExtractedFigure] = Field(default_factory=list)


EXTRACT_SYSTEM = """You extract financial figures from one page of an official company report.
- Extract the numeric line items of the financial tables on this page (at most 60), for every period column.
- Copy each number exactly as printed in `printed_value`. Do not convert units, digits or signs.
- Copy the table's unit line exactly in `unit_line`.
- Give the period of the column each number sits in. If you cannot tell which column a number belongs to, set uncertain=true.
- Do not invent figures. If the page has no financial table, return an empty list."""


@dataclass
class FigureCheck:
    evidence_id: str
    grounded: bool
    parse_reason: str | None
    scale: float | None
    reasons: list[str]


# How each company names itself on its pages, used to confirm vision transcriptions.
COMPANY_NAMES = {
    "COMI": ["Commercial International Bank", "CIB", "التجاري الدولي"],
    "ETEL": ["Telecom Egypt", "telecomegypt", "المصرية للاتصالات"],
    "TMGH": ["Talaat", "TMG", "طلعت مصطفى", "طلعت مصطفي"],
    "EFID": ["Edita", "إيديتا", "ايديتا"],
    "ABUK": ["Abu Qir", "Abou Kir", "Abu Kir", "أبوقير", "أبو قير", "ابوقير", "ابو قير"],
}


def expected_years(pdf: Path, sources: Path = Path("reports/SOURCES.json")) -> list[str]:
    """Years of the report's own period, from reports/SOURCES.json (e.g. '9M2026 ...' -> ['2026'])."""
    if not sources.exists():
        return []
    for s in json.loads(sources.read_text(encoding="utf-8")):
        if s.get("file") == pdf.name:
            years = re.findall(r"(?<!\d)20\d{2}(?!\d)", s.get("period", ""))
            return sorted(set(years))[-1:]  # the latest year: comparatives may be older
    return []


def _slug(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_") or "doc"


_EPS_SUBROWS = {"basic", "diluted", "basic and diluted", "الأساسي", "الاساسي", "المخفض", "الأساسية", "المخفضة"}


def row_kind(fig: ExtractedFigure, page: PageRecord) -> str | None:
    """figure_kind of a row, also catching 'Basic'/'Diluted' rows printed under an EPS heading."""
    kind = figure_kind(f"{fig.label} {fig.row_text}")
    if kind is None:
        label = re.sub(r"\((consolidated|separate|standalone)\)", "", normalize(fig.label).lower()).strip(" :-")
        if label in _EPS_SUBROWS and figure_kind(page.text) == "per_share":
            kind = "per_share"
    return kind


def check_figure(fig: ExtractedFigure, page: PageRecord, unit_line: str | None) -> tuple[float | None, float | None, list[str], bool, str | None]:
    """Return (value, scale, ambiguity reasons, grounded, parse reason)."""
    reasons = []
    printed = fig.printed_value.strip()
    if printed.startswith("(") and ")" not in printed and normalize(printed + ")") in normalize(page.text):
        printed += ")"  # the model dropped the closing bracket; the page shows it
    grounded = contains_number(page.text, printed)
    if not grounded:
        reasons.append("number not found in page text")
    parsed = parse_amount(printed)
    percent = printed.endswith("%")
    if parsed.uncertain:
        reasons.append(f"number unclear: {parsed.reason}")

    # The unit must be printed on the page; the model's unit line is only a pointer to it.
    line_scale = detect_scale(unit_line)[0] if unit_line else None
    page_scale, page_found = detect_scale(page.text)
    scale = None
    if not page_found:
        reasons.append("unit/scale not stated on page")
    elif page_scale is not None:
        scale = page_scale
        if line_scale is not None and line_scale != page_scale:
            reasons.append(f"unit line {unit_line!r} disagrees with page unit {page_found[0]!r}")
    elif line_scale is not None:
        scale = line_scale  # page mixes units; the table's own unit line decides, but flag it
        reasons.append(f"page shows several units {page_found}; relying on table unit line {unit_line!r}")
    else:
        reasons.append(f"conflicting units on page: {page_found}")

    if not fig.period:
        reasons.append("period not stated")
    if fig.uncertain:
        reasons.append("extractor marked uncertain" + (f": {fig.note}" if fig.note else ""))
    if page.method == "text" and any("Arabic text layer" in w for w in page.warnings):
        reasons.append("column/period order unverified (right-to-left text layer)")
    reasons += [w for w in page.warnings if w.startswith("unconfirmed transcription")]

    kind = row_kind(fig, page)
    if percent or kind:  # ratios, per-share figures, share counts: the page's money unit does not apply
        reasons = [r for r in reasons if "unit" not in r and "scale" not in r]
        scale = 1.0
    value = None if parsed.value is None or scale is None else parsed.value * scale
    return value, scale, reasons, grounded, parsed.reason


def extract_figures(doc: DocumentRecord, company: str, caller: Caller) -> tuple[list[EvidenceItem], list[FigureCheck]]:
    items, checks = [], []
    stem = _slug(Path(doc.path).stem)
    for page in doc.pages:
        if page.method == "none" or not page.text.strip():
            continue
        result: PageFigures = caller.structured(f"extract_p{page.page}", [
            SystemMessage(EXTRACT_SYSTEM),
            HumanMessage(f"Company: {company}\nPage {page.page} text:\n\n{page.text}"),
        ], PageFigures)
        for i, fig in enumerate(result.figures, 1):
            eid = f"{_slug(company)}-{stem}-p{page.page}-{i:02d}"
            value, scale, reasons, grounded, parse_reason = check_figure(fig, page, result.unit_line)
            ambiguous = bool(reasons) or value is None
            items.append(EvidenceItem(
                evidence_id=eid, company=company, document=Path(doc.path).name, page=page.page,
                label=fig.label + (f" ({fig.basis})" if fig.basis else ""),
                source_text=fig.row_text + (f" | unit: {result.unit_line}" if result.unit_line else ""),
                value=None if ambiguous else value,
                scale=scale or 1.0,
                currency=(None if fig.printed_value.strip().endswith("%") or row_kind(fig, page) == "count"
                          else (fig.currency or "EGP")),
                period=fig.period,
                status=EvidenceStatus.AMBIGUOUS if ambiguous else EvidenceStatus.VERIFIED,
                note="; ".join(reasons) or None,
            ))
            checks.append(FigureCheck(eid, grounded, parse_reason, scale, reasons))
    return items, checks


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pdf", type=Path, required=True)
    ap.add_argument("--company", required=True)
    ap.add_argument("--pages", help="e.g. 3-6,9 (default: all)")
    ap.add_argument("--mode", choices=["auto", "text", "vision"], default="auto")
    ap.add_argument("--provider", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--vision-provider", help="defaults to --provider")
    ap.add_argument("--vision-model", help="defaults to --model; use 'none' to disable vision")
    ap.add_argument("--base-url")
    ap.add_argument("--fallback", action="append", default=[], metavar="PROVIDER:MODEL",
                    help="model to use when the main one is overloaded or out of quota; repeatable, "
                         "e.g. openrouter:nvidia/nemotron-3.5-super-vl:free")
    ap.add_argument("--out", type=Path, default=Path("data/evidence"))
    a = ap.parse_args(argv)

    from .llm import make_fallback_chat
    caller = Caller(make_fallback_chat([f"{a.provider}:{a.model}", *a.fallback], a.base_url, temperature=0.0))
    vision = None
    if a.vision_model != "none" and a.mode != "text":
        main_vision = f"{a.vision_provider or a.provider}:{a.vision_model or a.model}"
        vision = Caller(make_fallback_chat([main_vision, *a.fallback], a.base_url, temperature=0.0))

    doc = read_pdf(a.pdf, parse_pages(a.pages), a.mode, vision,
                   expect=COMPANY_NAMES.get(a.company.upper()), expect_years=expected_years(a.pdf))
    items, checks = extract_figures(doc, a.company, caller)

    a.out.mkdir(parents=True, exist_ok=True)
    out = a.out / f"{_slug(a.company)}_{_slug(a.pdf.stem)}.json"
    out.write_text(json.dumps({
        "document": {"path": doc.path, "sha256": doc.sha256, "page_count": doc.page_count,
                     "pages": [asdict(p) for p in doc.pages]},
        "models": {"extract": [a.provider, a.model],
                   "vision": [a.vision_provider or a.provider, a.vision_model or a.model] if vision else None,
                   "fallback": a.fallback,
                   "answered_by": sorted({c.model for c in caller.calls + (vision.calls if vision else []) if c.model})},
        "evidence": [i.model_dump(mode="json") for i in items],
        "checks": [asdict(c) for c in checks],
        "calls": caller.log() + (vision.log() if vision else []),
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    verified = sum(i.status == EvidenceStatus.VERIFIED for i in items)
    print(f"{out}: {len(items)} figures, {verified} verified, {len(items) - verified} ambiguous; "
          f"pages: " + ", ".join(f"{p.page}:{p.method}" for p in doc.pages))


if __name__ == "__main__":
    main()
