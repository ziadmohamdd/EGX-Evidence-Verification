"""Hand-checked reference figures: the ground truth for the paper.

One author fills in a spreadsheet from the report PDFs; the other checks every
row against the PDF without looking at any system output. This module:

- ``template``: writes that spreadsheet, pre-filled with the figures to find
  in each report (value columns stored as text so Excel cannot reformat them);
- ``build``: reads the filled sheet, computes each value in base units (EGP,
  not thousands) with the same deterministic rules as the report reader, and
  writes ``figures.json``. Rows with problems are listed, never guessed;
- ``accuracy``: compares the report reader's output with the checked figures,
  so the reader's extraction accuracy can be reported.

Usage:
    python -m egx_guide.references template --out data/references/reference_sheet.xlsx
    python -m egx_guide.references build --sheet data/references/reference_sheet.xlsx \
        --out data/references/figures.json
    python -m egx_guide.references accuracy --figures data/references/figures.json \
        --evidence data/evidence

The guide for whoever fills in the sheet is docs/reference_answer_guide.md.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path

from pydantic import BaseModel

from .models import EvidenceItem, EvidenceStatus
from .numbers import detect_scale, normalize, parse_amount

REL_TOL = 0.005
LABEL_MATCH = 0.7  # label similarity needed to link an extracted figure to a reference row

COLUMNS = [
    # filled in by the template
    "figure_key", "company", "document", "page", "statement", "item",
    # filled in by the preparer
    "line_item_as_printed", "period_code", "period_as_printed", "printed_value", "unit_as_printed",
    "usable", "prepared_by", "preparer_note",
    # filled in by the checker
    "checked_by", "checker_agrees", "checker_note",
]
TEXT_COLUMNS = {"printed_value", "period_as_printed", "page", "period_code"}

# ---------------------------------------------------------------------------
# What to look for in each report
# ---------------------------------------------------------------------------

COMPANY_ITEMS = {
    "income statement": ["Revenue", "Gross profit", "Profit before tax", "Net profit for the period",
                         "Net profit attributable to owners of the parent", "Basic earnings per share"],
    "balance sheet": ["Total assets", "Total liabilities", "Total equity", "Cash and cash equivalents"],
}
BANK_ITEMS = {
    "income statement": ["Net interest income", "Net profit for the period",
                         "Net profit attributable to owners of the bank", "Basic earnings per share"],
    "balance sheet": ["Total assets", "Loans and advances to customers", "Customer deposits", "Total equity"],
}

# (company, document, items, {statement: page hint}, {statement: (current, comparative) period codes})
REPORTS = [
    ("COMI", "COMI_FY2025_consolidated_condensed_en.pdf", BANK_ITEMS,
     {"income statement": "5", "balance sheet": "4"},
     {"income statement": ("FY2025", "FY2024"), "balance sheet": ("31-12-2025", "31-12-2024")}),
    ("ETEL", "ETEL_FY2025_EAS_consolidated_en.pdf", COMPANY_ITEMS,
     {"income statement": "6", "balance sheet": "5"},
     {"income statement": ("FY2025", "FY2024"), "balance sheet": ("31-12-2025", "31-12-2024")}),
    ("TMGH", "TMGH_FY2025_consolidated_en.pdf", COMPANY_ITEMS,
     {"income statement": "7", "balance sheet": "5-6"},
     {"income statement": ("FY2025", "FY2024"), "balance sheet": ("31-12-2025", "31-12-2024")}),
    ("TMGH", "TMGH_FY2025_results_summary_ar.pdf", COMPANY_ITEMS,
     {"income statement": "1", "balance sheet": "1"},
     {"income statement": ("FY2025", "FY2024"), "balance sheet": ("31-12-2025", "31-12-2024")}),
    ("EFID", "EFID_FY2025_EAS_consolidated_signed_en.pdf", COMPANY_ITEMS,
     {"income statement": "6", "balance sheet": "5"},
     {"income statement": ("FY2025", "FY2024"), "balance sheet": ("31-12-2025", "31-12-2024")}),
    ("ABUK", "ABUK_9M2026_results.pdf", COMPANY_ITEMS,
     {"income statement": "", "balance sheet": ""},
     {"income statement": ("9M2026", "9M2025"), "balance sheet": ("30-09-2026", "31-12-2025")}),
]


def _slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def template_rows() -> list[dict]:
    rows = []
    for company, document, items, pages, periods in REPORTS:
        lang = "ar" if document.endswith("_ar.pdf") or company == "ABUK" else "en"
        for statement, names in items.items():
            for period in periods[statement]:
                for name in names:
                    rows.append({c: "" for c in COLUMNS} | {
                        "figure_key": f"{company}-{lang}-{_slug(name)}-{period}",
                        "company": company, "document": document, "page": pages[statement],
                        "statement": statement, "item": name, "period_code": period,
                    })
    return rows


# ---------------------------------------------------------------------------
# The spreadsheet
# ---------------------------------------------------------------------------


def write_template(path: Path, rows: list[dict] | None = None) -> Path:
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.worksheet.datavalidation import DataValidation

    rows = template_rows() if rows is None else rows
    wb = Workbook()
    ws = wb.active
    ws.title = "figures"
    ws.append(COLUMNS)
    for r in rows:
        ws.append([str(r.get(c, "") or "") for c in COLUMNS])

    groups = {"figure_key": "DDDDDD", "line_item_as_printed": "DDEBF7", "checked_by": "E2EFDA"}
    fill = None
    for i, name in enumerate(COLUMNS, 1):
        fill = groups.get(name, None) or fill
        cell = ws.cell(row=1, column=i)
        cell.font = Font(bold=True)
        cell.fill = PatternFill("solid", fgColor=fill)
        cell.alignment = Alignment(wrap_text=True, vertical="top")
        width = {"figure_key": 34, "document": 34, "item": 30, "line_item_as_printed": 36,
                 "preparer_note": 30, "checker_note": 30}.get(name, 16)
        ws.column_dimensions[ws.cell(row=1, column=i).column_letter].width = width
        if name in TEXT_COLUMNS:  # stop Excel turning "(1,234)" into -1234 or dates into serials
            for row in ws.iter_rows(min_row=2, max_row=max(len(rows) + 1, 500), min_col=i, max_col=i):
                row[0].number_format = "@"
    ws.freeze_panes = "C2"

    n = max(len(rows) + 1, 500)
    for col, choices in (("usable", "yes,no"), ("checker_agrees", "yes,no")):
        dv = DataValidation(type="list", formula1=f'"{choices}"', allow_blank=True)
        letter = ws.cell(row=1, column=COLUMNS.index(col) + 1).column_letter
        dv.add(f"{letter}2:{letter}{n}")
        ws.add_data_validation(dv)

    path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(path)
    return path


def read_sheet(path: Path) -> list[dict]:
    from openpyxl import load_workbook

    ws = load_workbook(path, read_only=True, data_only=True).active
    it = ws.iter_rows(values_only=True)
    header = [str(h).strip() if h is not None else "" for h in next(it)]
    missing = [c for c in COLUMNS if c not in header]
    if missing:
        raise ValueError(f"{path}: missing columns {missing}")
    rows = []
    for values in it:
        r = {h: ("" if v is None else str(v).strip()) for h, v in zip(header, values)}
        if r.get("figure_key"):
            rows.append(r)
    return rows


# ---------------------------------------------------------------------------
# Building the checked figures
# ---------------------------------------------------------------------------


class RefFigure(BaseModel):
    figure_key: str
    company: str
    document: str
    pages: list[int] | None
    statement: str
    line_item: str
    period_code: str
    period_as_printed: str | None
    printed_value: str | None
    unit: str | None
    value: float | None
    usable: bool
    note: str | None = None
    prepared_by: str | None = None
    checked_by: str | None = None


def _pages(spec: str) -> list[int] | None:
    nums = [int(n) for n in re.findall(r"\d+", spec or "")]
    if not nums:
        return None
    if "-" in spec and len(nums) == 2:
        return list(range(nums[0], nums[1] + 1))
    return nums


def _yes(s: str) -> bool | None:
    s = (s or "").strip().lower()
    return True if s in ("yes", "y", "true", "1", "نعم") else False if s in ("no", "n", "false", "0", "لا") else None


def build_figures(rows: list[dict], require_checked: bool = True) -> tuple[list[RefFigure], list[str]]:
    """Turn filled rows into checked figures. Returns (figures, problems)."""
    figures, problems = [], []
    for r in rows:
        key = r["figure_key"]
        printed = (r.get("printed_value") or "").strip()
        usable = _yes(r.get("usable", ""))
        usable = True if usable is None and printed else usable
        if not printed and usable is not False:
            continue  # not filled in yet

        notes = "; ".join(n for n in (r.get("preparer_note"), r.get("checker_note")) if n) or None
        checked = bool(r.get("checked_by")) and _yes(r.get("checker_agrees", "")) is True
        if _yes(r.get("checker_agrees", "")) is False:
            problems.append(f"{key}: checker and preparer disagree ({r.get('checker_note') or 'no note'})")
            continue
        if require_checked and not checked:
            problems.append(f"{key}: not checked yet (checked_by / checker_agrees)")
            continue

        value = None
        unit = (r.get("unit_as_printed") or "").strip() or None
        if usable:
            parsed = parse_amount(printed)
            if parsed.uncertain:
                problems.append(f"{key}: value {printed!r} cannot be read ({parsed.reason}); "
                                "fix it or mark usable=no with a note")
                continue
            if printed.endswith("%"):
                scale = 1.0
            else:
                scale = detect_scale(unit or "")[0]
                if scale is None:
                    problems.append(f"{key}: unit {unit!r} missing or unclear; write it as printed, "
                                    "e.g. 'EGP thousands', 'L.E. (000)', 'بالألف جنيه', 'EGP'")
                    continue
            value = parsed.value * scale

        figures.append(RefFigure(
            figure_key=key, company=r["company"], document=r["document"], pages=_pages(r.get("page", "")),
            statement=r.get("statement", ""), line_item=r.get("line_item_as_printed") or r.get("item", ""),
            period_code=r.get("period_code", ""), period_as_printed=r.get("period_as_printed") or None,
            printed_value=printed or None, unit=unit, value=value, usable=bool(usable), note=notes,
            prepared_by=r.get("prepared_by") or None, checked_by=(r.get("checked_by") or None) if checked else None,
        ))
    return figures, problems


# ---------------------------------------------------------------------------
# Reader accuracy
# ---------------------------------------------------------------------------


def _label(s: str) -> str:
    s = normalize(s).lower()
    s = re.sub(r"\((consolidated|separate|standalone)\)\s*$", "", s)
    return re.sub(r"[^\w]+", " ", s).strip()


def _years(s: str | None) -> set[str]:
    return set(re.findall(r"(?<!\d)(?:19|20)\d{2}(?!\d)", normalize(s or "")))


def _same_period(fig: RefFigure, item: EvidenceItem) -> bool:
    want = _years(fig.period_as_printed) or _years(fig.period_code)
    got = _years(item.period)
    if not want or not got:
        return False
    return want <= got if len(want) == 1 else want == got


def _close(a: float, b: float) -> bool:
    return abs(a - b) <= REL_TOL * max(abs(b), 1e-9)


def compare_extraction(items: list[EvidenceItem], figures: list[RefFigure]) -> list[dict]:
    """For each checked figure, what did the reader do with it?

    correct             a verified extracted figure has the right value
    wrong_but_verified  the reader marked it verified with a wrong value (the dangerous case)
    flagged_ambiguous   only ambiguous extractions: safe, but not usable
    missing             nothing extracted that matches document, page, period and label
    verified_but_unusable  the reference says do not use, yet the reader verified it
    """
    out = []
    for fig in figures:
        candidates = []
        for it in items:
            if it.document != fig.document or not _same_period(fig, it):
                continue
            if fig.pages and it.page not in fig.pages:
                continue
            score = SequenceMatcher(None, _label(fig.line_item), _label(it.label)).ratio()
            if score >= LABEL_MATCH:
                candidates.append((score, it))
        best = max((s for s, _ in candidates), default=0)
        matched = [it for s, it in candidates if s == best]
        verified = [it for it in matched if it.status is EvidenceStatus.VERIFIED and it.value is not None]

        if not matched:
            outcome = "missing"
        elif not fig.usable:
            outcome = "verified_but_unusable" if verified else "flagged_ambiguous"
        elif not verified:
            outcome = "flagged_ambiguous"
        elif all(_close(it.value, fig.value) for it in verified):
            outcome = "correct"
        else:
            outcome = "wrong_but_verified"
        out.append({
            "figure_key": fig.figure_key, "document": fig.document, "outcome": outcome,
            "reference_value": fig.value, "evidence_ids": [it.evidence_id for it in matched],
            "extracted_values": [it.value for it in verified],
        })
    return out


OUTCOMES = ["correct", "wrong_but_verified", "flagged_ambiguous", "missing", "verified_but_unusable"]


def accuracy_table(results: list[dict]) -> str:
    docs = sorted({r["document"] for r in results})
    lines = ["| Document | " + " | ".join(OUTCOMES) + " |", "|---" * (len(OUTCOMES) + 1) + "|"]
    for d in docs:
        c = Counter(r["outcome"] for r in results if r["document"] == d)
        lines.append(f"| {d} | " + " | ".join(str(c[o]) for o in OUTCOMES) + " |")
    return "\n".join(lines)


def load_evidence(folder: Path) -> list[EvidenceItem]:
    items = []
    for f in sorted(folder.glob("*.json")):
        data = json.loads(f.read_text(encoding="utf-8"))
        items += [EvidenceItem.model_validate(e) for e in data.get("evidence", [])]
    return items


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("template", help="write the spreadsheet to fill in")
    t.add_argument("--out", type=Path, default=Path("data/references/reference_sheet.xlsx"))
    b = sub.add_parser("build", help="filled sheet -> figures.json")
    b.add_argument("--sheet", type=Path, required=True)
    b.add_argument("--out", type=Path, default=Path("data/references/figures.json"))
    b.add_argument("--allow-unchecked", action="store_true", help="development only: include rows not yet checked")
    a = sub.add_parser("accuracy", help="compare the report reader's output with the checked figures")
    a.add_argument("--figures", type=Path, default=Path("data/references/figures.json"))
    a.add_argument("--evidence", type=Path, default=Path("data/evidence"))
    a.add_argument("--out", type=Path, help="also save the per-figure results as JSON")
    args = ap.parse_args(argv)

    if args.cmd == "template":
        if args.out.exists():
            raise SystemExit(f"{args.out} already exists; it may hold filled-in work. Choose another --out.")
        print(write_template(args.out))
    elif args.cmd == "build":
        figures, problems = build_figures(read_sheet(args.sheet), require_checked=not args.allow_unchecked)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps([f.model_dump() for f in figures], indent=2, ensure_ascii=False),
                            encoding="utf-8")
        print(f"{args.out}: {len(figures)} figures, {len(problems)} problems")
        for p in problems:
            print("  -", p)
    else:
        figures = [RefFigure.model_validate(f) for f in json.loads(args.figures.read_text(encoding="utf-8"))]
        results = compare_extraction(load_evidence(args.evidence), figures)
        print(accuracy_table(results))
        if args.out:
            args.out.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
