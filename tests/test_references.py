import json

import pytest

from egx_guide.models import EvidenceItem, EvidenceStatus
from egx_guide.references import (
    build_figures,
    compare_extraction,
    main,
    read_sheet,
    template_rows,
    write_template,
)


def row(**kw):
    base = {
        "figure_key": "COMI-net_profit-FY2025", "company": "COMI", "document": "COMI.pdf",
        "page": "5", "statement": "income statement", "item": "Net profit",
        "line_item_as_printed": "Net profit for the year", "period_code": "FY2025",
        "period_as_printed": "Dec. 31, 2025", "printed_value": "55,123", "unit_as_printed": "EGP thousands",
        "usable": "yes", "prepared_by": "A", "preparer_note": "", "checked_by": "B",
        "checker_agrees": "yes", "checker_note": "",
    }
    return {**base, **kw}


def test_template_covers_every_report_with_unique_keys():
    rows = template_rows()
    keys = [r["figure_key"] for r in rows]
    assert len(keys) == len(set(keys))
    docs = {r["document"] for r in rows}
    assert {"COMI_FY2025_consolidated_condensed_en.pdf", "ABUK_9M2026_results.pdf",
            "TMGH_FY2025_results_summary_ar.pdf"} <= docs
    assert any(r["item"] == "Customer deposits" for r in rows if r["company"] == "COMI")
    assert all(r["printed_value"] == "" for r in rows)


def test_sheet_round_trip_keeps_numbers_as_printed(tmp_path):
    path = tmp_path / "sheet.xlsx"
    write_template(path, [row(printed_value="(1,234)"), row(figure_key="k2", printed_value="٥٥٬١٢٣")])
    back = read_sheet(path)
    assert [r["printed_value"] for r in back] == ["(1,234)", "٥٥٬١٢٣"]
    assert back[0]["figure_key"] == "COMI-net_profit-FY2025"


@pytest.mark.parametrize("printed, unit, value", [
    ("55,123", "EGP thousands", 55_123_000),
    ("(1,234)", "L.E. (000)", -1_234_000),
    ("٥٥٬١٢٣", "بالألف جنيه", 55_123_000),
    ("18.25", "EGP per share", 18.25),
    ("33.4%", "EGP thousands", 33.4),
    ("12,969,606,637", "Egyptian pound", 12_969_606_637),
    ("٪٤٦", "العملة بالجنية المصرى", 46),
    ("%(٤)", "", -4),
    ("٪٥٩,٦", "", 59.6),
])
def test_values_are_computed_from_printed_number_and_unit(printed, unit, value):
    [f], problems = build_figures([row(printed_value=printed, unit_as_printed=unit)])
    assert problems == [] and f.value == pytest.approx(value) and f.usable


def test_change_rows_are_read_as_percent_even_without_the_sign():
    [f], problems = build_figures([row(period_code="change-9M", printed_value="(12)", unit_as_printed="مليون جنيه")])
    assert problems == [] and f.value == -12


def test_template_has_quarter_and_change_rows_where_printed():
    keys = {r["figure_key"] for r in template_rows()}
    assert {"ABUK-ar-revenue-Q3-2026", "ABUK-ar-revenue-change-9M", "ABUK-ar-revenue-change-Q3",
            "TMGH-ar-basic_earnings_per_share-change-FY"} <= keys


def test_per_share_row_with_thousands_unit_is_a_problem():
    _, problems = build_figures([row(item="Basic earnings per share", line_item_as_printed="Basic",
                                     printed_value="18.25", unit_as_printed="EGP thousands")])
    assert "per share" in problems[0]


def test_share_count_needs_no_currency():
    [f], problems = build_figures([row(item="Weighted average number of shares",
                                       line_item_as_printed="عدد الأسهم", printed_value="3,000,000",
                                       unit_as_printed="")])
    assert problems == [] and f.value == 3_000_000


def test_problems_are_reported_and_rows_left_out():
    rows = [
        row(figure_key="a", unit_as_printed=""),
        row(figure_key="b", printed_value="8?0"),
        row(figure_key="c", checker_agrees="no", checker_note="page shows 55,128"),
        row(figure_key="d", printed_value=""),  # not filled in yet: skipped quietly
        row(figure_key="e", printed_value="", usable="no", preparer_note="digit hidden by stamp"),
    ]
    figs, problems = build_figures(rows)
    assert [f.figure_key for f in figs] == ["e"] and figs[0].usable is False and figs[0].value is None
    text = "\n".join(problems)
    assert "a:" in text and "unit" in text
    assert "b:" in text and "illegible" in text
    assert "c:" in text and "disagree" in text
    assert "d:" not in text


def test_unchecked_rows_need_a_flag():
    rows = [row(checked_by="", checker_agrees="")]
    figs, problems = build_figures(rows)
    assert figs == [] and "not checked" in problems[0]
    figs, problems = build_figures(rows, require_checked=False)
    assert len(figs) == 1 and figs[0].checked_by is None


def ev(eid, label, period, value, status=EvidenceStatus.VERIFIED, page=5, doc="COMI.pdf"):
    return EvidenceItem(evidence_id=eid, company="COMI", document=doc, page=page, label=label,
                        source_text="x", value=value if status is EvidenceStatus.VERIFIED else None,
                        period=period, status=status)


def test_reader_accuracy_against_hand_checked_figures():
    figs, _ = build_figures([
        row(figure_key="np25"),                                                       # read correctly
        row(figure_key="np24", period_code="FY2024", period_as_printed="Dec. 31, 2024",
            printed_value="48,900"),                                                  # verified but wrong
        row(figure_key="ta25", line_item_as_printed="Total assets", printed_value="1,250,000",
            page="4"),                                                                # flagged ambiguous
        row(figure_key="eps", line_item_as_printed="Basic earnings per share", printed_value="18.25",
            unit_as_printed="EGP"),                                                   # not extracted
    ])
    items = [
        ev("e1", "Net profit for the year (consolidated)", "Dec. 31, 2025", 55_123_000),
        ev("e2", "Net profit for the year (consolidated)", "Dec. 31, 2024", 48_900),  # scale error
        ev("e3", "Total assets", "Dec. 31, 2025", None, EvidenceStatus.AMBIGUOUS, page=4),
        ev("e4", "Revenue", "Dec. 31, 2025", 9e9),                                     # no reference: ignored
    ]
    res = {r["figure_key"]: r for r in compare_extraction(items, figs)}
    assert res["np25"]["outcome"] == "correct" and res["np25"]["evidence_ids"] == ["e1"]
    assert res["np24"]["outcome"] == "wrong_but_verified"
    assert res["ta25"]["outcome"] == "flagged_ambiguous"
    assert res["eps"]["outcome"] == "missing"


def test_period_and_page_must_match():
    [f], _ = build_figures([row()])
    wrong_year = ev("e1", "Net profit for the year", "Dec. 31, 2024", 55_123_000)
    wrong_page = ev("e2", "Net profit for the year", "Dec. 31, 2025", 55_123_000, page=9)
    no_year = ev("e3", "Net profit for the year", None, 55_123_000)
    [r] = compare_extraction([wrong_year, wrong_page, no_year], [f])
    assert r["outcome"] == "missing"


def test_cli_build_and_accuracy(tmp_path, capsys):
    sheet, figs_json, ev_dir = tmp_path / "s.xlsx", tmp_path / "figures.json", tmp_path / "ev"
    write_template(sheet, [row()])
    main(["build", "--sheet", str(sheet), "--out", str(figs_json)])
    assert json.loads(figs_json.read_text(encoding="utf-8"))[0]["value"] == 55_123_000

    ev_dir.mkdir()
    (ev_dir / "COMI.json").write_text(json.dumps({"evidence": [
        ev("e1", "Net profit for the year", "Dec. 31, 2025", 55_123_000).model_dump(mode="json")]}))
    main(["accuracy", "--figures", str(figs_json), "--evidence", str(ev_dir)])
    out = capsys.readouterr().out
    assert "COMI.pdf" in out and "correct" in out
