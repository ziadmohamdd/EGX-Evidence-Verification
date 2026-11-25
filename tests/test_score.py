import json
from pathlib import Path

import pytest

from egx_guide.models import Action
from egx_guide.score import (
    ClaimVerdict,
    ReferenceAnswer,
    load_references,
    main,
    score_record,
    score_run,
    summarise,
)

CASES_DIR = Path(__file__).parent / "fixtures" / "cases"

REF = ReferenceAnswer.model_validate({
    "case_id": "c1",
    "figures": {
        "np": {"value": 1_250e6},
        "rev": {"value": None, "usable": False, "note": "illegible digit"},
        "eq": {"value": 9_000e6},
    },
    "acceptable_actions": ["hold", "keep_cash"],
})


def rec(claims=(), action="hold", unused=(), ticker="SYNA", shares=0):
    return {
        "action": action, "ticker": ticker, "shares": shares, "explanation": "x",
        "claims": [{"evidence_id": e, "stated_value": v, "statement": "s"} for e, v in claims],
        "unused_figures": list(unused), "limitations": [],
    }


def record(final, proposed=None, condition="A", case_id="c1", violations=(), blocked=False, verifier=None):
    return {
        "case_id": case_id, "condition": condition, "status": "ok",
        "proposed": proposed or final, "final": final, "blocked": blocked,
        "violations": list(violations), "verifier": verifier, "calls": [], "seconds": 1.0,
    }


def verdicts(s):
    return [c.verdict for c in s.final.claims]


def test_claims_are_judged_against_the_reference_not_the_evidence_store():
    s = score_record(record(rec([("np", 1_250e6), ("np", 1.25e9), ("np", 1_250), ("rev", 800e6), ("zz", 1)])), REF)
    assert verdicts(s) == [ClaimVerdict.CORRECT, ClaimVerdict.CORRECT, ClaimVerdict.WRONG_VALUE,
                           ClaimVerdict.AMBIGUOUS_USED, ClaimVerdict.UNKNOWN]
    assert s.final.n_claims == 5 and s.final.n_correct == 2 and s.final.n_incorrect == 3
    assert s.final.claim_precision == pytest.approx(0.4)
    assert s.final.has_incorrect


def test_scale_errors_are_labelled():
    [c] = score_record(record(rec([("np", 1_250)])), REF).final.claims
    assert c.scale_error == 1e6


def test_coverage_counts_distinct_usable_figures_cited_correctly():
    s = score_record(record(rec([("np", 1_250e6), ("np", 1_250e6)])), REF)
    assert s.final.usable_reference_figures == 2
    assert s.final.coverage == pytest.approx(0.5)


def test_no_claims_gives_no_precision_but_zero_coverage():
    s = score_record(record(rec(action="insufficient_evidence", ticker=None)), REF)
    assert s.final.claim_precision is None and s.final.coverage == 0
    assert not s.final.has_incorrect
    assert s.action_acceptable is False and s.insufficient_evidence


def test_action_and_portfolio_outcomes():
    s = score_record(record(rec(action="buy", shares=10), violations=[{"rule": "cash"}], blocked=True), REF)
    assert s.action_acceptable is False and s.n_violations == 1 and s.blocked
    assert score_record(record(rec(action="keep_cash")), REF).action_acceptable is True


def test_proposed_is_scored_separately_from_final():
    s = score_record(record(final=rec([("np", 1_250e6)]), proposed=rec([("np", 1_250)]),
                            verifier={"dropped": [], "revised": True}), REF)
    assert s.proposed.n_incorrect == 1 and s.final.n_incorrect == 0
    assert s.verifier_revised and s.verifier_dropped == 0


def test_withdrawn_figures_count_as_dropped():
    s = score_record(record(final=rec(), proposed=rec([("np", 1_250)]),
                            verifier={"dropped": ["np"], "withdrawn": ["np", "rev"], "revised": True}), REF)
    assert s.verifier_dropped == 2  # np once, plus rev withdrawn by the revision


def test_missing_reference_and_errors_are_kept_but_not_scored():
    s = score_record(record(rec([("np", 1)]), case_id="other"), None)
    assert s.scored is False and s.reason == "no_reference"
    e = score_record({"case_id": "c1", "condition": "A", "status": "error", "error": "boom"}, REF)
    assert e.scored is False and e.reason == "run_error"


def test_summary_reports_accuracy_and_coverage_per_condition():
    rows = [
        score_record(record(rec([("np", 1_250e6)]), condition="A"), REF),
        score_record(record(rec([("np", 1_250)]), condition="A"), REF),
        score_record({"case_id": "c1", "condition": "A", "status": "error", "error": "x"}, REF),
        score_record(record(rec([("np", 1_250e6), ("eq", 9e9)]), condition="B"), REF),
    ]
    summ = {r["condition"]: r for r in summarise(rows)}
    a, b = summ["A"], summ["B"]
    assert a["records"] == 3 and a["scored"] == 2 and a["run_errors"] == 1
    assert a["claims"] == 2 and a["incorrect_claims"] == 1
    assert a["incorrect_claim_rate"] == pytest.approx(0.5)
    assert a["share_with_incorrect_claim"] == pytest.approx(0.5)
    assert a["mean_coverage"] == pytest.approx(0.25)
    assert b["incorrect_claim_rate"] == 0 and b["mean_coverage"] == 1


def test_reference_rejects_usable_figure_without_value():
    with pytest.raises(ValueError):
        ReferenceAnswer.model_validate({"case_id": "x", "figures": {"a": {"value": None}},
                                        "acceptable_actions": [Action.HOLD]})


def test_end_to_end_on_a_run_folder(tmp_path, capsys):
    run_dir, refs = tmp_path / "run", tmp_path / "refs"
    (run_dir / "A").mkdir(parents=True)
    refs.mkdir()
    (run_dir / "manifest.json").write_text("{}")
    (run_dir / "A" / "c1.json").write_text(json.dumps(record(rec([("np", 1_250e6)]))))
    (refs / "c1.json").write_text(REF.model_dump_json())

    assert set(load_references(refs)) == {"c1"}
    rows = score_run(run_dir, load_references(refs))
    assert len(rows) == 1 and rows[0].final.n_correct == 1

    main([str(run_dir), "--references", str(refs)])
    out = json.loads((run_dir / "scores.json").read_text(encoding="utf-8"))
    assert out["summary"][0]["condition"] == "A" and len(out["records"]) == 1
    assert (run_dir / "summary.csv").exists()
    assert "| A |" in capsys.readouterr().out


# ------------------------------------------- text figures and decision measures


def with_text(r, text):
    return {**r, "explanation": text}


def test_uncited_and_wrong_scale_figures_in_text_are_counted():
    final = with_text(rec([("eq", 9_000e6)]), "Profit was 1.25 billion; equity 9 billion; profit again 1,250 pounds.")
    s = score_record(record(final), REF)
    assert [t["evidence_id"] for t in s.final.text_uncited] == ["np"]
    assert [t["evidence_id"] for t in s.final.text_wrong_scale] == ["np"]
    assert s.final.text_wrong_scale[0]["scale_error"] == 1e6


def test_cited_text_figures_are_not_counted():
    s = score_record(record(with_text(rec([("np", 1_250e6)]), "Profit was 1.25 billion.")), REF)
    assert s.final.text_uncited == [] and s.final.text_wrong_scale == []


def test_decision_without_figures_is_flagged_but_refusal_is_not():
    assert score_record(record(rec(action="hold")), REF).no_figure_decision
    assert not score_record(record(rec(action="keep_cash")), REF).no_figure_decision
    assert not score_record(record(rec([("np", 1_250e6)], action="hold")), REF).no_figure_decision


def test_concentrated_buy_uses_the_portfolio_after_the_trade():
    from egx_guide.models import Case
    case = Case.model_validate_json(next((CASES_DIR).glob("*.json")).read_text(encoding="utf-8"))
    ticker = next(iter(case.prices))
    price = case.prices[ticker]

    def buy(shares, cash):
        r = record(rec(action="buy", ticker=ticker, shares=shares))
        r["proposed_portfolio"] = {"cash": cash, "currency": "EGP", "holdings": [{"ticker": ticker, "shares": shares}]}
        return score_record(r, REF, case=case)

    big, small = buy(100, 10.0), buy(10, 100 * price)
    assert big.concentrated_buy and big.concentration > 0.99
    assert not small.concentrated_buy and small.concentration < 0.1
    assert score_record(record(rec(action="hold")), REF, case=case).concentration is None
