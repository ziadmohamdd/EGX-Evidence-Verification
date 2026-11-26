import json

import pytest

from egx_guide.references import write_template
from egx_guide.sheetcheck import load_ai_notes, main, run, sheet_checks, supplies_value, text_checks
from .pdf_factory import scanned_pdf, text_pdf


def row(item="Revenue", period="FY2025", printed="1,000", doc="X.pdf", page="1", **kw):
    base = {
        "figure_key": f"{doc}-{item}-{period}", "company": "XCO", "document": doc, "page": page,
        "statement": "income statement", "item": item, "line_item_as_printed": item,
        "period_code": period, "period_as_printed": period, "printed_value": printed,
        "unit_as_printed": "EGP thousands", "usable": "yes", "prepared_by": "ZM", "preparer_note": "",
        "checked_by": "", "checker_agrees": "", "checker_note": "",
    }
    return {**base, **kw}


def flags(checks, item, period="FY2025", doc="X.pdf"):
    return checks[f"{doc}-{item}-{period}"].flags


def test_clean_rows_have_no_flags():
    checks = sheet_checks([row(), row(period="FY2024", printed="800"),
                           row(period="change-FY", printed="25%", unit_as_printed="")])
    assert all(c.flags == [] for c in checks.values())
    assert checks["X.pdf-Revenue-FY2025"].value == 1_000_000
    assert sheet_checks([row(printed="")]) == {}  # not filled in yet


def test_change_in_percent_must_fit_the_two_period_values():
    checks = sheet_checks([row(), row(period="FY2024", printed="800"),
                           row(period="change-FY", printed="52%", unit_as_printed="")])
    assert any("change in %" in f for f in flags(checks, "Revenue", "change-FY"))


def test_balance_sheet_and_gross_profit_identities():
    bs = [row(item=i, printed=v, statement="balance sheet") for i, v in
          (("Total assets", "1,000"), ("Total liabilities", "600"), ("Total equity", "300"))]
    checks = sheet_checks(bs + [row(), row(item="Gross profit", printed="1,200")])
    assert all(any("liabilities + total equity" in f for f in flags(checks, i))
               for i in ("Total assets", "Total liabilities", "Total equity"))
    assert any("larger than revenue" in f for f in flags(checks, "Gross profit"))
    ok = sheet_checks([row(item="Total assets", printed="1,000"), row(item="Total liabilities", printed="600"),
                       row(item="Total equity", printed="400")])
    assert all(c.flags == [] for c in ok.values())


def test_quarter_larger_than_nine_months_and_unit_slips():
    checks = sheet_checks([row(period="9M2026", printed="900"), row(period="Q3-2026", printed="950"),
                           row(period="FY2025", printed="1,000"), row(period="FY2024", printed="1")])
    assert any("columns swapped" in f for f in flags(checks, "Revenue", "Q3-2026"))
    assert any("20 times" in f for f in flags(checks, "Revenue", "FY2025"))
    assert any("20 times" in f for f in flags(checks, "Revenue", "FY2024"))


def test_same_figure_in_two_reports_and_units_on_one_page():
    checks = sheet_checks([row(printed="1,000"), row(doc="Y.pdf", printed="1.1", unit_as_printed="EGP millions"),
                           row(item="Gross profit", printed="400", unit_as_printed="EGP millions")])
    assert any("Y.pdf" in f for f in flags(checks, "Revenue"))
    assert any("unit differs" in f for f in flags(checks, "Gross profit"))


def test_missing_columns_and_unusable_rows_need_notes():
    checks = sheet_checks([row(period_as_printed="", page=""),
                           row(item="Gross profit", printed="", usable="no")])
    assert {"period as printed is empty", "page is empty"} <= set(flags(checks, "Revenue"))
    assert flags(checks, "Gross profit") == ["marked not usable without a note saying why"]


def test_text_layer_checks(tmp_path):
    text_pdf(tmp_path / "X.pdf", [["Income statement  EGP thousands", "Revenue 6 1 000 500", "Gross profit 400"],
                                   ["Notes to the statements  EGP thousands", "Other operating income 77,777"]])
    scanned_pdf(tmp_path / "S.pdf")
    checks = sheet_checks([
        row(printed="1,000,500"),                                    # spaces as separators, note 6 before it
        row(item="Gross profit", printed="4,000"),                    # not on the page
        row(item="Other income", printed="77,777"),                    # on page 2, sheet says 1
        row(item="Net profit", printed="400", unit_as_printed="EGP millions"),
        row(doc="S.pdf", printed="99", company="S"),                             # scan: left to the image check
        row(item="Total equity", page="9"),
    ])
    text_checks(checks, tmp_path)
    assert flags(checks, "Revenue") == []
    assert any("not found" in f for f in flags(checks, "Gross profit"))
    assert any("on page 2" in f for f in flags(checks, "Other income"))
    assert any("unit line" in f for f in flags(checks, "Net profit"))
    assert any("line item" in f for f in flags(checks, "Net profit"))
    assert flags(checks, "Revenue", doc="S.pdf") == []
    assert any("does not exist" in f for f in flags(checks, "Total equity"))


@pytest.mark.parametrize("note, bad", [
    ("value looks like the 2024 column", False), ("unit line on page 5 says millions", False),
    ("Q3 and 9M columns may be swapped", False), ("should be 1,234", True), ("off by 3 digits", True),
])
def test_ai_notes_never_carry_a_value(note, bad):
    assert supplies_value(note) is bad


def test_ai_notes_are_validated(tmp_path):
    p = tmp_path / "ai.json"
    p.write_text(json.dumps({"k": {"verdict": "disagrees", "fields": ["value"], "note": "it is 55"}}))
    with pytest.raises(ValueError, match="contains a figure"):
        load_ai_notes(p, {"k"})
    p.write_text(json.dumps({"other": {"verdict": "agrees"}}))
    with pytest.raises(ValueError, match="not a filled row"):
        load_ai_notes(p, {"k"})
    p.write_text(json.dumps({"k": {"verdict": "maybe"}}))
    with pytest.raises(ValueError, match="verdict"):
        load_ai_notes(p, {"k"})


def test_run_writes_review_page_images_and_flags(tmp_path, capsys):
    reports = tmp_path / "reports"
    reports.mkdir()
    text_pdf(reports / "X.pdf", [["EGP thousands", "Revenue 1,000", "Gross profit 400"]])
    sheet = tmp_path / "sheet.xlsx"
    write_template(sheet, [row(), row(item="Gross profit", printed="500")])
    out = tmp_path / "check"
    (out).mkdir()
    (out / "ai_notes.json").write_text(json.dumps({
        "X.pdf-Revenue-FY2025": {"verdict": "agrees"},
        "X.pdf-Gross profit-FY2025": {"verdict": "disagrees", "fields": ["value"], "note": "digits differ"}}))
    main(["--sheet", str(sheet), "--reports", str(reports), "--out", str(out)])
    assert "2 filled rows, 1 flagged" in capsys.readouterr().out
    s = json.loads((out / "flags.json").read_text(encoding="utf-8"))
    assert s["ai_disagrees"] == 1 and list(s["rows"]) == ["X.pdf-Gross profit-FY2025"]
    page = (out / "review.html").read_text(encoding="utf-8")
    assert "pages/X_p1.png" in page and "digits differ" in page
    assert (out / "pages" / "X_p1.png").stat().st_size > 1000
    assert run(sheet, reports, out, images=False)["filled_rows"] == 2
