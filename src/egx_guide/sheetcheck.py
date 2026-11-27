"""Check the filled reference sheet against the report pages, before the figures are used.

The sheet is the ground truth, so its mistakes would be scored as the agents'.
This helper never looks at system output (evidence, runs) and never supplies a
value. It uses only the sheet and the report PDFs:

- **page images**: every page a filled row points to is rendered as a PNG, and
  ``review.html`` shows each page beside the rows read from it, so the author
  can re-read a flagged row in seconds;
- **plain-code checks** on the author's own values: the change in % against the
  two period values, assets against liabilities plus equity, gross profit
  against revenue, three months against nine months, the two Talaat Moustafa
  reports against each other, units on the same page, and, where the page has a
  text layer, whether the printed number, unit and line item are on that page;
- **AI-assisted notes** (``ai_notes.json``): a reviewer compares each row with
  the page image and records whether it agrees. Notes may say *what* looks
  wrong (value, unit, period, line item) but never the right number; a note
  with a figure in it is refused.

Usage:
    python -m egx_guide.sheetcheck --sheet data/references/reference_sheet.xlsx \
        --reports reports --out data/references/check

The author then re-reads the PDF for every flagged row and fills in the green
columns (docs/reference_answer_guide.md).
"""

from __future__ import annotations

import argparse
import html
import json
import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

from .numbers import arabic_ratio, detect_scale, figure_kind, normalize
from .references import _pages, build_figures, read_sheet

RENDER_SCALE = 2.0       # 144 dpi, as the reader uses
CHANGE_TOL_POINTS = 1.5  # printed % changes are rounded; allow for that
BALANCE_TOL = 0.005      # assets vs liabilities + equity
SAME_FIGURE_TOL = 0.01   # one figure in two reports (rounded to millions in the summary)
PERIOD_RATIO = 20        # two periods of one item differing more than this suggests a unit or digit slip
MIN_TEXT_CHARS = 40
ARABIC_PAGE_RATIO = 0.3

CHANGE_PAIRS = {"change-FY": ("FY2025", "FY2024"), "change-9M": ("9M2026", "9M2025"),
                "change-Q3": ("Q3-2026", "Q3-2025")}
QUARTER_OF = {"Q3-2026": "9M2026", "Q3-2025": "9M2025"}
VERDICTS = ("agrees", "disagrees", "unclear")
FIELDS = ("value", "unit", "period", "line item", "page", "usable")


@dataclass
class RowCheck:
    key: str
    row: dict
    value: float | None = None
    flags: list[str] = field(default_factory=list)
    ai: dict | None = None

    @property
    def flagged(self) -> bool:
        return bool(self.flags) or bool(self.ai and self.ai.get("verdict") != "agrees")


def filled(rows: list[dict]) -> list[dict]:
    return [r for r in rows if (r.get("printed_value") or "").strip() or (r.get("usable") or "").lower() == "no"]


# ---------------------------------------------------------------------------
# Plain-code checks on the sheet itself
# ---------------------------------------------------------------------------


def _scale(r: dict) -> float | None:
    if (r.get("printed_value") or "").count("%") or "٪" in (r.get("printed_value") or "") \
            or (r.get("period_code") or "").startswith("change"):
        return None
    if figure_kind(f"{r.get('item', '')} {r.get('line_item_as_printed', '')}") in ("per_share", "count"):
        return None
    return detect_scale(r.get("unit_as_printed") or "")[0]


def sheet_checks(rows: list[dict]) -> dict[str, RowCheck]:
    checks = {r["figure_key"]: RowCheck(r["figure_key"], r) for r in filled(rows)}
    figures, problems = build_figures([c.row for c in checks.values()], require_checked=False)
    for f in figures:
        checks[f.figure_key].value = f.value
    for p in problems:
        key, _, msg = p.partition(": ")
        if key in checks:
            checks[key].flags.append(msg)

    for c in checks.values():
        r = c.row
        if (r.get("usable") or "").lower() == "no":
            if not (r.get("preparer_note") or "").strip():
                c.flags.append("marked not usable without a note saying why")
            continue
        for col, what in (("line_item_as_printed", "line item as printed"),
                          ("period_as_printed", "period as printed"), ("unit_as_printed", "unit as printed")):
            if not (r.get(col) or "").strip() and not (col == "unit_as_printed" and _scale(r) is None):
                c.flags.append(f"{what} is empty")
        if not _pages(r.get("page", "")):
            c.flags.append("page is empty")

    # index: (document, item, period) -> check
    by = {(c.row["document"], c.row["item"], c.row["period_code"]): c for c in checks.values()}

    def val(doc, item, period):
        c = by.get((doc, item, period))
        return c.value if c else None

    for (doc, item, period), c in by.items():
        if c.value is None:
            continue
        # the printed change in % against the two period values on the sheet
        if period in CHANGE_PAIRS:
            cur, prev = (val(doc, item, p) for p in CHANGE_PAIRS[period])
            if cur is not None and prev:
                diff = abs((cur - prev) / abs(prev) * 100 - c.value)
                if diff > CHANGE_TOL_POINTS:
                    c.flags.append(f"the change in % is {diff:.0f} points away from what the two period values "
                                   f"on the sheet give: check the % and both values")
            continue
        # three months can't exceed nine months of the same year (for positive flows)
        if period in QUARTER_OF:
            nine = val(doc, item, QUARTER_OF[period])
            if nine is not None and c.value > 0 and nine > 0 and c.value > nine * 1.001:
                c.flags.append(f"three-month value is larger than the nine-month value ({QUARTER_OF[period]}): "
                               "columns swapped?")
        # two periods of one item far apart: a unit or digit slip (either row may be the wrong one)
        if period not in QUARTER_OF:
            for other in sorted({p for (d, i, p) in by if d == doc and i == item}):
                o = val(doc, item, other)
                if other <= period or other in CHANGE_PAIRS or other in QUARTER_OF or not o or not c.value:
                    continue
                ratio = abs(c.value / o)
                if ratio > PERIOD_RATIO or ratio < 1 / PERIOD_RATIO:
                    c.flags.append(f"differs more than {PERIOD_RATIO} times from {other}: check digits and unit")
                    by[(doc, item, other)].flags.append(
                        f"differs more than {PERIOD_RATIO} times from {period}: check digits and unit")

    # balance sheet and income statement identities, per document and period
    for doc, period in {(d, p) for (d, _, p) in by if p not in CHANGE_PAIRS}:
        assets, liab, equity = (val(doc, i, period) for i in ("Total assets", "Total liabilities", "Total equity"))
        if None not in (assets, liab, equity) and assets and abs(assets - liab - equity) > BALANCE_TOL * abs(assets):
            for i in ("Total assets", "Total liabilities", "Total equity"):
                by[(doc, i, period)].flags.append("total assets ≠ total liabilities + total equity on the sheet")
        rev, gp = val(doc, "Revenue", period), val(doc, "Gross profit", period)
        if rev is not None and gp is not None and rev > 0 and gp > rev:
            by[(doc, "Gross profit", period)].flags.append("gross profit is larger than revenue")

    # one figure in two reports of the same company (Talaat Moustafa: statements and Arabic summary)
    by_company = defaultdict(list)
    for c in checks.values():
        if c.value is not None and not c.row["period_code"].startswith("change"):
            by_company[(c.row["company"], c.row["item"], c.row["period_code"])].append(c)
    for group in by_company.values():
        docs = {c.row["document"] for c in group}
        if len(docs) < 2:
            continue
        for c in group:
            for o in group:
                if o.row["document"] != c.row["document"] and o.value and \
                        abs(c.value - o.value) > SAME_FIGURE_TOL * abs(o.value):
                    c.flags.append(f"differs from the same figure in {o.row['document']}")

    # units: rows read from the same page should share the unit
    by_page = defaultdict(list)
    for c in checks.values():
        s = _scale(c.row)
        if s is not None:
            for p in _pages(c.row.get("page", "")) or []:
                by_page[(c.row["document"], p, c.row["statement"])].append((s, c))
    for items in by_page.values():
        scales = [s for s, _ in items]
        common = max(set(scales), key=scales.count)
        for s, c in items:
            if s != common and "unit differs from the other rows read from this page" not in c.flags:
                c.flags.append("unit differs from the other rows read from this page")
    return checks


# ---------------------------------------------------------------------------
# Checks against the page's own text layer, where it has one
# ---------------------------------------------------------------------------

_TOKEN = re.compile(r"\d{1,3}(?:[ ,]\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?")


def _digits(s: str) -> str:
    """'(1,234.5)' and '1 234.5' -> '1234.5'."""
    return re.sub(r"[^\d.]", "", normalize(s)).strip(".")


def page_numbers(text: str) -> set[str]:
    """Every number on the page, digits only.

    Where spaces separate thousands ('106 672 946'), a note number before the
    amount ('6 107 699') reads as one token, so every run of whole groups counts.
    """
    out = set()
    for tok in _TOKEN.findall(normalize(text)):
        parts = tok.split(" ")
        out |= {_digits(" ".join(parts[i:j])) for i in range(len(parts)) for j in range(i + 1, len(parts) + 1)}
    return out


def _label(s: str) -> str:
    return re.sub(r"[^\w]+", " ", normalize(s).lower()).strip()


def text_checks(checks: dict[str, RowCheck], reports: Path) -> dict[tuple[str, int], str]:
    """Flag rows whose number, unit or line item isn't on the page's text layer.

    Pages without a usable text layer (scans) or with an Arabic layer (reading
    order unreliable) are left to the image check. Returns the page texts used.
    """
    import pypdfium2 as pdfium

    texts: dict[tuple[str, int], str] = {}
    by_doc = defaultdict(list)
    for c in checks.values():
        by_doc[c.row["document"]].append(c)
    for doc, cs in by_doc.items():
        path = reports / doc
        if not path.exists():
            for c in cs:
                c.flags.append(f"report not found: {path}")
            continue
        pdf = pdfium.PdfDocument(str(path))
        try:
            n_pages = len(pdf)

            def text(n: int) -> str | None:
                if (doc, n) not in texts:
                    tp = pdf[n - 1].get_textpage()
                    texts[(doc, n)] = tp.get_text_range() or ""
                    tp.close()
                t = texts[(doc, n)]
                usable = sum(not ch.isspace() for ch in t) >= MIN_TEXT_CHARS and arabic_ratio(t) < ARABIC_PAGE_RATIO
                return t if usable else None

            for c in cs:
                pages = _pages(c.row.get("page", "")) or []
                bad = [p for p in pages if not 1 <= p <= n_pages]
                if bad:
                    c.flags.append(f"page {bad[0]} does not exist ({n_pages} pages)")
                    continue
                layers = [(p, text(p)) for p in pages]
                layers = [(p, t) for p, t in layers if t is not None]
                printed = (c.row.get("printed_value") or "").strip()
                if not layers or not printed:
                    continue
                needle = _digits(printed.replace("%", "").replace("٪", ""))
                if needle and not any(needle in page_numbers(t) for _, t in layers):
                    elsewhere = [p for p in range(1, n_pages + 1) if p not in pages and len(needle) >= 5
                                 and (t := text(p)) is not None and needle in page_numbers(t)]
                    c.flags.append("printed number not found on the page's text layer"
                                   + (f" (it is on page {elsewhere[0]})" if elsewhere else ""))
                s = _scale(c.row)
                page_scale = detect_scale(" ".join(t for _, t in layers))[0]
                if s is not None and page_scale is not None and s != page_scale:
                    c.flags.append("unit differs from the unit line in the page's text layer")
                lab = _label(c.row.get("line_item_as_printed") or "")
                if lab and not any(lab in _label(t) for _, t in layers):
                    c.flags.append("line item as printed not found on the page's text layer (spelling?)")
        finally:
            pdf.close()
    return texts


# ---------------------------------------------------------------------------
# AI-assisted notes: agreement only, never a value
# ---------------------------------------------------------------------------


def supplies_value(note: str) -> bool:
    """A note may name a page or a year column, nothing else with digits."""
    t = re.sub(r"\bpages?\s+\d+", "", normalize(note), flags=re.I)
    t = re.sub(r"\b(19|20)\d{2}\b", "", t)
    t = re.sub(r"\b(Q[1-4]|[39]M)\b", "", t, flags=re.I)
    return bool(re.search(r"\d", t))


def load_ai_notes(path: Path | None, keys: set[str]) -> dict[str, dict]:
    if not path or not path.exists():
        return {}
    notes = json.loads(path.read_text(encoding="utf-8"))
    for key, n in notes.items():
        if key not in keys:
            raise ValueError(f"{path}: {key} is not a filled row of the sheet")
        if n.get("verdict") not in VERDICTS:
            raise ValueError(f"{path}: {key}: verdict must be one of {VERDICTS}")
        bad = [f for f in n.get("fields", []) if f not in FIELDS]
        if bad:
            raise ValueError(f"{path}: {key}: unknown fields {bad}; use {FIELDS}")
        if supplies_value(n.get("note", "")):
            raise ValueError(f"{path}: {key}: the note contains a figure; say what looks wrong, not the value")
    return notes


# ---------------------------------------------------------------------------
# Page images and the review page
# ---------------------------------------------------------------------------


def page_image_name(document: str, page: int) -> str:
    return f"{Path(document).stem}_p{page}.png"


def render_pages(checks: dict[str, RowCheck], reports: Path, out: Path) -> list[Path]:
    import pypdfium2 as pdfium

    wanted = defaultdict(set)
    for c in checks.values():
        for p in _pages(c.row.get("page", "")) or []:
            wanted[c.row["document"]].add(p)
    (out / "pages").mkdir(parents=True, exist_ok=True)
    made = []
    for doc, pages in wanted.items():
        if not (reports / doc).exists():
            continue
        pdf = pdfium.PdfDocument(str(reports / doc))
        try:
            for p in sorted(pages):
                if not 1 <= p <= len(pdf):
                    continue
                target = out / "pages" / page_image_name(doc, p)
                if not target.exists():
                    pdf[p - 1].render(scale=RENDER_SCALE).to_pil().save(target)
                made.append(target)
        finally:
            pdf.close()
    return made


SHOW = ["figure_key", "line_item_as_printed", "period_code", "period_as_printed", "printed_value",
        "unit_as_printed", "usable", "preparer_note"]


def _fmt(v: float | None) -> str:
    return "" if v is None else f"{v:,.2f}".rstrip("0").rstrip(".")


def review_html(checks: dict[str, RowCheck], out: Path) -> Path:
    groups = defaultdict(list)
    for c in checks.values():
        pages = _pages(c.row.get("page", "")) or [0]
        groups[(c.row["document"], tuple(pages))].append(c)
    n_flag = sum(c.flagged for c in checks.values())
    parts = [f"""<!doctype html><html><head><meta charset="utf-8"><title>Reference sheet check</title>
<style>
body{{font:14px/1.45 system-ui,sans-serif;margin:16px;background:#fafafa;color:#222}}
h2{{margin-top:40px;border-top:2px solid #ccc;padding-top:12px}}
.wrap{{display:flex;gap:16px;align-items:flex-start;flex-wrap:wrap}}
.imgs{{flex:1 1 640px;max-height:90vh;overflow:auto;border:1px solid #ccc;background:#fff}}
.imgs img{{width:100%;display:block}}
table{{border-collapse:collapse;flex:1 1 520px;font-size:13px;background:#fff}}
td,th{{border:1px solid #ddd;padding:4px 6px;vertical-align:top;text-align:left}}
tr.flag{{background:#fff3cd}} .flags{{color:#a33}} .ai{{color:#245}}
.num{{font-family:Consolas,monospace;white-space:nowrap}}
</style></head><body>
<h1>Reference sheet check</h1>
<p>{len(checks)} filled rows, <b>{n_flag} flagged</b>. Yellow rows need a second look at the page.
Re-read the PDF for each, then fill in the green columns of the sheet.
"In pounds" is your printed value times your unit, so a wrong unit shows there.</p>"""]
    for (doc, pages), cs in sorted(groups.items()):
        title = f"{doc}, page {'–'.join(map(str, (pages[0], pages[-1]))) if len(pages) > 1 else pages[0]}"
        parts.append(f"<h2>{html.escape(title)}</h2><div class='wrap'><div class='imgs'>")
        for p in pages:
            if p and (out / "pages" / page_image_name(doc, p)).exists():
                parts.append(f"<img loading='lazy' src='pages/{page_image_name(doc, p)}' alt='page {p}'>")
        parts.append("</div><table><tr>" + "".join(f"<th>{h}</th>" for h in SHOW)
                     + "<th>in pounds</th><th>to check</th></tr>")
        for c in sorted(cs, key=lambda c: (c.row["statement"], c.row["item"], c.row["period_code"])):
            cells = "".join(f"<td class='{'num' if h == 'printed_value' else ''}'>"
                            f"{html.escape(str(c.row.get(h, '')))}</td>" for h in SHOW)
            notes = "".join(f"<div class='flags'>• {html.escape(f)}</div>" for f in c.flags)
            if c.ai:
                notes += (f"<div class='ai'>AI check: <b>{html.escape(c.ai['verdict'])}</b>"
                          + (f" ({', '.join(map(html.escape, c.ai.get('fields', [])))})" if c.ai.get("fields") else "")
                          + (f": {html.escape(c.ai.get('note', ''))}" if c.ai.get("note") else "") + "</div>")
            parts.append(f"<tr class='{'flag' if c.flagged else ''}'>{cells}"
                         f"<td class='num'>{_fmt(c.value)}</td><td>{notes}</td></tr>")
        parts.append("</table></div>")
    parts.append("</body></html>")
    path = out / "review.html"
    path.write_text("".join(parts), encoding="utf-8")
    return path


def summary(checks: dict[str, RowCheck]) -> dict:
    ai = [c.ai for c in checks.values() if c.ai]
    return {
        "filled_rows": len(checks),
        "flagged_rows": sum(c.flagged for c in checks.values()),
        "flagged_by_code": sum(bool(c.flags) for c in checks.values()),
        "ai_checked": len(ai),
        "ai_disagrees": sum(a["verdict"] == "disagrees" for a in ai),
        "ai_unclear": sum(a["verdict"] == "unclear" for a in ai),
        "rows": {k: {"flags": c.flags, "ai": c.ai} for k, c in sorted(checks.items()) if c.flagged},
    }


def run(sheet: Path, reports: Path, out: Path, ai_notes: Path | None = None, images: bool = True) -> dict:
    checks = sheet_checks(read_sheet(sheet))
    text_checks(checks, reports)
    for key, note in load_ai_notes(ai_notes, set(checks)).items():
        checks[key].ai = note
    out.mkdir(parents=True, exist_ok=True)
    if images:
        render_pages(checks, reports, out)
    review_html(checks, out)
    s = summary(checks)
    (out / "flags.json").write_text(json.dumps(s, ensure_ascii=False, indent=2), encoding="utf-8")
    return s


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--sheet", type=Path, default=Path("data/references/reference_sheet.xlsx"))
    ap.add_argument("--reports", type=Path, default=Path("reports"))
    ap.add_argument("--out", type=Path, default=Path("data/references/check"))
    ap.add_argument("--ai-notes", type=Path, help="default: <out>/ai_notes.json if it exists")
    ap.add_argument("--no-images", action="store_true", help="skip rendering the page images")
    a = ap.parse_args(argv)
    s = run(a.sheet, a.reports, a.out, a.ai_notes or a.out / "ai_notes.json", images=not a.no_images)
    print(f"{s['filled_rows']} filled rows, {s['flagged_rows']} flagged "
          f"({s['flagged_by_code']} by the plain-code checks, {s['ai_disagrees']} AI disagreements, "
          f"{s['ai_unclear']} unclear). Open {a.out / 'review.html'}")
    for key, r in s["rows"].items():
        for f in r["flags"]:
            print(f"  {key}: {f}")
        if r["ai"] and r["ai"]["verdict"] != "agrees":
            print(f"  {key}: AI check {r['ai']['verdict']} {r['ai'].get('fields', [])}")


if __name__ == "__main__":
    main()
