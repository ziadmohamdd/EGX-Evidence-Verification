import json

import pytest

from egx_guide.cases import CaseSpec, build_case, main, template_figures
from egx_guide.models import EvidenceItem, EvidenceStatus
from egx_guide.references import RefFigure

DOC = "COMI_FY2025.pdf"


def ev(eid, label, period, value, status=EvidenceStatus.VERIFIED, page=5, company="COMI", doc=DOC, row=None):
    return EvidenceItem(evidence_id=eid, company=company, document=doc, page=page, label=label,
                        source_text=row or f"row of {eid}", value=value if status is EvidenceStatus.VERIFIED else None,
                        period=period, status=status, note=None if status is EvidenceStatus.VERIFIED else "unclear")


ITEMS = [
    ev("e1", "Net profit for the year (consolidated)", "Dec. 31, 2025", 55_123_000),
    ev("e2", "Net profit for the year (consolidated)", "Dec. 31, 2024", 48_900),          # reader scale error
    ev("e3", "Total assets", "Dec. 31, 2025", None, EvidenceStatus.AMBIGUOUS, page=4),
    ev("e4", "Revenue", "Dec. 31, 2025", 9e9),                                           # not chosen
    ev("x1", "Net profit", "31 December 2025", 2_000_000_000, company="EFID", doc="EFID.pdf", page=6),
]


def fig(key, line, period, value, usable=True, page=5, company="COMI", doc=DOC):
    return RefFigure(figure_key=key, company=company, document=doc, pages=[page], statement="",
                     line_item=line, period_code=period, period_as_printed=None, printed_value=None,
                     unit=None, value=value, usable=usable, checked_by="B")


BANK = {f.figure_key: f for f in [
    fig("np25", "Net profit for the year", "FY2025", 55_123_000),
    fig("np24", "Net profit for the year", "FY2024", 48_900_000),
    fig("ta25", "Total assets", "31-12-2025", 1_250_000_000, page=4),
    fig("eps25", "Basic earnings per share", "FY2025", 18.25),
    fig("efid_np", "Net profit", "FY2025", 2_000_000_000, company="EFID", doc="EFID.pdf", page=6),
]}

PRICES = {"2026-11-18": {"COMI": {"price": 80.5, "source": "egx.com.eg"},
                         "EFID": {"price": 30.0, "source": "egx.com.eg"}}}


def spec(**kw):
    base = {
        "case_id": "dev_001", "split": "dev", "information_cutoff": "2026-11-18",
        "profile": {"goal": "grow savings", "horizon": "3-5 years", "liquidity_needs": "low",
                    "loss_willingness": "medium", "loss_capacity": "medium"},
        "portfolio": {"cash": 50_000, "holdings": [{"ticker": "COMI", "shares": 100}]},
        "figures": ["np25", "np24", "ta25"],
        "acceptable_actions": ["hold", "keep_cash"],
    }
    return CaseSpec.model_validate({**base, **kw})


def test_case_uses_only_chosen_figures_with_true_values_as_reference():
    case, ref, problems = build_case(spec(), ITEMS, BANK, PRICES)
    assert problems == []
    assert [e.evidence_id for e in case.evidence] == ["e1", "e2", "e3"]
    assert case.prices == {"COMI": 80.5}
    # the reader's scale error stays in the evidence; the reference holds the checked value
    assert ref.figures["e2"].value == 48_900_000 and ref.figures["e1"].value == 55_123_000
    assert ref.figures["e3"].usable and ref.figures["e3"].value == 1_250_000_000
    assert ref.case_id == "dev_001" and [a.value for a in ref.acceptable_actions] == ["hold", "keep_cash"]


def test_column_headings_are_added_from_the_hand_checked_file():
    cols = {(DOC, 5): "Notes | Dec. 31, 2025 | Dec. 31, 2024"}
    case, _, problems = build_case(spec(), ITEMS, BANK, PRICES, columns=cols)
    assert problems == []
    by_id = {e.evidence_id: e for e in case.evidence}
    assert by_id["e1"].columns == by_id["e2"].columns == "Notes | Dec. 31, 2025 | Dec. 31, 2024"
    assert by_id["e3"].columns is None  # page 4 has no entry
    assert ITEMS[0].columns is None  # the reader's output is not changed


def test_reader_column_headings_win_over_the_file():
    items = [ITEMS[0].model_copy(update={"columns": "Note | 2025 | 2024"}), *ITEMS[1:]]
    case, _, _ = build_case(spec(), items, BANK, PRICES, columns={(DOC, 5): "other"})
    assert case.evidence[0].columns == "Note | 2025 | 2024"


ROW = "Revenue | 6 | 9,000,000 | 7,500,000 | 20%"
NEIGHBOURS = [
    ev("r25", "Revenue", "Dec. 31, 2025", 9e9, row=ROW + " | unit: EGP thousands"),
    ev("r24", "Revenue", "Dec. 31, 2024", 7.5e9, row=ROW + " | unit: EGP thousands"),
    ev("rch", "Revenue", "change (%)", None, EvidenceStatus.AMBIGUOUS, row=ROW + " | unit: EGP thousands"),
    ev("o25", "Revenue", "Dec. 31, 2025", 1.0, page=6, row=ROW),  # same text, other page: not a neighbour
]
REV = {**BANK, "rev25": fig("rev25", "Revenue", "FY2025", 9e9), "rev24": fig("rev24", "Revenue", "FY2024", 7.5e9)}


def test_other_numbers_in_a_chosen_row_get_their_own_ids_outside_coverage():
    case, ref, problems = build_case(spec(figures=["rev25"]), NEIGHBOURS, REV, PRICES, provisional=True)
    assert problems == []
    assert [e.evidence_id for e in case.evidence] == ["r25", "r24", "rch"]  # neighbours right after their figure
    assert ref.figures["r25"].in_coverage
    assert ref.figures["r24"].value == 7.5e9 and ref.figures["r24"].usable and not ref.figures["r24"].in_coverage
    assert not ref.figures["rch"].usable  # an unreadable neighbour stays unusable


def test_a_chosen_figure_is_not_demoted_to_a_neighbour():
    case, ref, _ = build_case(spec(figures=["rev25", "rev24"]), NEIGHBOURS, REV, PRICES, provisional=True)
    assert [e.evidence_id for e in case.evidence] == ["r25", "rch", "r24"]  # chosen figures keep the spec's order
    assert ref.figures["r24"].in_coverage and not ref.figures["rch"].in_coverage


def test_neighbours_use_hand_checked_values_or_are_reported():
    case, ref, problems = build_case(spec(figures=["rev25"]), NEIGHBOURS, REV, PRICES)
    assert ref.figures["r24"].value == 7.5e9 and not ref.figures["r24"].in_coverage  # matched rev24 on the sheet
    assert "rch" not in ref.figures and [e.evidence_id for e in case.evidence] == ["r25", "r24"]
    assert len(problems) == 1 and "rch" in problems[0] and "reference sheet" in problems[0]


def test_coverage_ignores_neighbours():
    from egx_guide.score import ReferenceAnswer, ReferenceFigure, score_recommendation
    ref = ReferenceAnswer(case_id="x", acceptable_actions=["hold"], figures={
        "r25": ReferenceFigure(value=9e9), "r24": ReferenceFigure(value=7.5e9, in_coverage=False)})
    s = score_recommendation({"claims": [{"evidence_id": "r25", "stated_value": 9e9},
                                         {"evidence_id": "r24", "stated_value": 7.5e9}]}, ref)
    assert s.usable_reference_figures == 1 and s.covered == 1 and s.n_incorrect == 0


def test_hand_read_figures_join_their_row_as_neighbours(tmp_path):
    from egx_guide.cases import load_added_evidence
    path = tmp_path / "added.json"
    path.write_text(json.dumps([{"row_of": "r25", "period": "التغير %", "printed": "٪٢٠", "value": 20}]),
                    encoding="utf-8")
    added = load_added_evidence(path, NEIGHBOURS[:2])
    assert [a.evidence_id for a in added] == ["r25-chg"]
    a = added[0]
    assert a.value == 20 and a.currency is None and a.status is EvidenceStatus.VERIFIED and "٪٢٠" in a.note
    assert a.source_text == NEIGHBOURS[0].source_text and NEIGHBOURS[0].evidence_id == "r25"  # reader item unchanged
    case, ref, problems = build_case(spec(figures=["rev25"]), NEIGHBOURS[:2] + added, REV, PRICES, provisional=True)
    assert [e.evidence_id for e in case.evidence] == ["r25", "r24", "r25-chg"]
    assert ref.figures["r25-chg"].value == 20 and not ref.figures["r25-chg"].in_coverage


def test_hand_read_figure_must_name_a_reader_row(tmp_path):
    from egx_guide.cases import load_added_evidence
    path = tmp_path / "added.json"
    path.write_text(json.dumps([{"row_of": "nope", "period": "change %", "printed": "5%", "value": 5}]))
    with pytest.raises(ValueError, match="nope"):
        load_added_evidence(path, NEIGHBOURS)
    assert load_added_evidence(tmp_path / "missing.json", NEIGHBOURS) == []


def test_missing_figure_and_unknown_key_are_problems():
    case, ref, problems = build_case(spec(figures=["np25", "eps25", "nope"]), ITEMS, BANK, PRICES)
    assert [e.evidence_id for e in case.evidence] == ["e1"]
    text = "\n".join(problems)
    assert "eps25" in text and "reader" in text
    assert "nope" in text and "reference" in text


def test_missing_price_stops_the_case():
    case, ref, problems = build_case(spec(figures=["efid_np"]), ITEMS, BANK, {"2026-11-18": {"COMI": PRICES["2026-11-18"]["COMI"]}})
    assert case is None and any("EFID" in p and "price" in p for p in problems)


def test_prices_cover_portfolio_and_evidence_companies():
    case, _, problems = build_case(spec(figures=["np25", "efid_np"]), ITEMS, BANK, PRICES)
    assert problems == [] and case.prices == {"COMI": 80.5, "EFID": 30.0}


def test_trap_makes_a_figure_unreadable_in_evidence_and_reference():
    s = spec(trap="unreadable", make_ambiguous={"np25": "last digit hidden by a stamp"})
    case, ref, problems = build_case(s, ITEMS, BANK, PRICES)
    e1 = next(e for e in case.evidence if e.evidence_id == "e1")
    assert e1.status is EvidenceStatus.AMBIGUOUS and e1.value is None and "stamp" in e1.note
    assert ref.figures["e1"].usable is False


def test_label_override_helps_matching():
    s = spec(figures=[{"key": "np25", "label": "Net profit for the year"}])
    bank = {"np25": BANK["np25"].model_copy(update={"line_item": "Profit after tax"})}
    case, _, problems = build_case(s, ITEMS, bank, PRICES)
    assert problems == [] and [e.evidence_id for e in case.evidence] == ["e1"]


TEMPLATE = [
    {"figure_key": "np25", "company": "COMI", "document": DOC, "page": "5", "statement": "income statement",
     "item": "Net profit for the year", "period_code": "FY2025"},
    {"figure_key": "np24", "company": "COMI", "document": DOC, "page": "5", "statement": "income statement",
     "item": "Net profit for the year", "period_code": "FY2024"},
    {"figure_key": "ta25", "company": "COMI", "document": DOC, "page": "4", "statement": "balance sheet",
     "item": "Total assets", "period_code": "31-12-2025"},
]


def test_test_cases_cannot_use_provisional_references():
    with pytest.raises(ValueError, match="provisional"):
        build_case(spec(split="test"), ITEMS, template_figures(TEMPLATE), PRICES, provisional=True)


def test_provisional_references_use_sheet_keys_and_reader_values():
    case, ref, problems = build_case(spec(), ITEMS, template_figures(TEMPLATE), PRICES, provisional=True)
    assert problems == [] and [e.evidence_id for e in case.evidence] == ["e1", "e2", "e3"]
    assert ref.figures["e1"].value == 55_123_000
    assert ref.figures["e2"].value == 48_900          # the reader's value, errors included: hence PROVISIONAL
    assert ref.figures["e3"].usable is False
    assert "PROVISIONAL" in ref.prepared_by


def test_default_template_keys_are_available():
    assert "COMI-en-net_profit_for_the_period-FY2025" in template_figures()


def test_cli_writes_case_and_reference(tmp_path):
    (tmp_path / "specs").mkdir()
    (tmp_path / "evidence").mkdir()
    (tmp_path / "specs" / "dev_001.json").write_text(spec().model_dump_json())
    (tmp_path / "evidence" / "COMI.json").write_text(json.dumps({"evidence": [e.model_dump(mode="json") for e in ITEMS]}))
    (tmp_path / "figures.json").write_text(json.dumps([f.model_dump() for f in BANK.values()]))
    (tmp_path / "prices.json").write_text(json.dumps(PRICES))
    main(["--specs", str(tmp_path / "specs"), "--evidence", str(tmp_path / "evidence"),
          "--figures", str(tmp_path / "figures.json"), "--prices", str(tmp_path / "prices.json"),
          "--added", str(tmp_path / "none.json"), "--out", str(tmp_path / "out")])
    case = json.loads((tmp_path / "out" / "cases" / "dev" / "dev_001.json").read_text(encoding="utf-8"))
    ref = json.loads((tmp_path / "out" / "references" / "cases" / "dev_001.json").read_text(encoding="utf-8"))
    assert case["case_id"] == "dev_001" and len(case["evidence"]) == 3
    assert ref["figures"]["e2"]["value"] == 48_900_000
