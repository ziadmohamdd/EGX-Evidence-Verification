import pytest

from egx_guide.score import RecordScore, RecScore
from egx_guide.stats import analyse, compare, holm, mcnemar_majority, per_case, repeatability


def rs(case, cond, wrong, scored=True):
    claims = []
    if wrong is not None:
        from egx_guide.score import ClaimVerdict, ScoredClaim
        claims = [ScoredClaim("x", 1.0, 2.0 if wrong else 1.0,
                              ClaimVerdict.WRONG_VALUE if wrong else ClaimVerdict.CORRECT)]
    s = RecScore(claims, usable_reference_figures=1, covered=0 if wrong else 1)
    return RecordScore(case_id=case, condition=cond, scored=scored, reason=None if scored else "run_error",
                       proposed=s if scored else None, final=s if scored else None, action="hold",
                       action_acceptable=True)


def repeat(pattern):
    """pattern: {condition: [wrong? per case]}"""
    return [rs(f"c{i}", cond, w) for cond, ws in pattern.items() for i, w in enumerate(ws)]


def test_per_case_averages_repeats_and_compare_is_paired():
    reps = [repeat({"A": [1, 1, 0, 1], "B": [0, 1, 0, 0]}), repeat({"A": [1, 0, 0, 1], "B": [0, 0, 0, 0]})]
    vals = per_case(reps, "wrong_figure")
    assert vals["A"] == {"c0": 1.0, "c1": 0.5, "c2": 0.0, "c3": 1.0}
    r = compare(vals, "B", "A")
    assert r["n_cases"] == 4 and r["mean_difference"] == pytest.approx(-(1.0 + 0.0 + 0 + 1.0) / 4)
    lo, hi = r["ci95"]
    assert lo <= r["mean_difference"] <= hi <= 0


def test_no_difference_gives_p_one():
    reps = [repeat({"A": [0, 0, 1], "B": [0, 0, 1]})]
    assert compare(per_case(reps, "wrong_figure"), "B", "A")["p_wilcoxon"] == 1.0


def test_holm_adjusts_in_order_and_keeps_none():
    assert holm([0.01, 0.04, None]) == [0.02, 0.04, None]
    assert holm([0.03, 0.02]) == [0.04, 0.04]


def test_failed_runs_count_as_wrong_only_in_the_sensitivity_check():
    reps = [repeat({"A": [0, 0]}) + [rs("c0", "B", None, scored=False), rs("c1", "B", False)]]
    assert per_case(reps, "wrong_figure")["B"] == {"c1": 0.0}
    assert per_case(reps, "wrong_figure", failed_as_wrong=True)["B"] == {"c0": 1.0, "c1": 0.0}


def test_mcnemar_and_repeatability():
    reps = [repeat({"A": [1, 1, 1, 0], "B": [0, 0, 1, 0]}), repeat({"A": [1, 1, 0, 0], "B": [0, 0, 1, 0]}),
            repeat({"A": [1, 0, 1, 0], "B": [0, 0, 1, 0]})]
    m = mcnemar_majority(reps, "A", "B")
    assert m["only_A_wrong"] == 2 and m["only_B_wrong"] == 0
    rep = repeatability(reps)
    assert rep["A"] == {"cases": 4, "disagree": 2} and rep["B"] == {"cases": 4, "disagree": 0}


def test_analyse_reports_every_measure_with_primary_and_interaction():
    reps = [repeat({c: [1, 0, 1, 0, 1] for c in "ABCD"})]
    res = analyse(reps)
    wf = res["measures"]["wrong_figure"]
    assert [r["comparison"] for r in wf["primary"]] == ["B - A", "D - C"]
    assert wf["exploratory"][-1]["comparison"] == "(B - A) - (D - C)"
    assert all("p_holm" in r for r in wf["primary"])
    assert set(res["measures"]) >= {"wrong_figure", "coverage", "acceptable_action"}
