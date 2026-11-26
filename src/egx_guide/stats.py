"""The paper's statistics (docs/evaluation_plan.md §5): paired comparisons between conditions.

Each run folder is one repeat of the same cases. Every record is scored against the
reference answers, then the repeats of a case under a condition are averaged, giving one
value per case and condition. Conditions are compared **paired by case**:

- primary (H1): B vs A and D vs C, Holm-corrected;
- exploratory: C vs A and D vs B (H2), and the interaction (B - A) - (D - C) (H3).

For each comparison: the mean per-case difference with a 95% bootstrap confidence interval
(10,000 resamples of cases, fixed seed) and a two-sided Wilcoxon signed-rank test. As
sensitivity checks the primary measure is also given with failed runs counted as wrong,
with an exact McNemar test on each case's majority outcome, and at other score tolerances.
Repeatability is the share of cases whose repeats disagree.

Usage:
    python -m egx_guide.stats runs/<repeat1> runs/<repeat2> runs/<repeat3> \
        --references data/references/cases --cases data/cases/test --out docs/results/stats.json
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from statistics import mean

from scipy.stats import binomtest, wilcoxon

from .models import Case
from .score import SCORE_REL_TOL, RecordScore, load_references, score_run

N_BOOT = 10_000
SEED = 20261126
PRIMARY = [("B", "A"), ("D", "C")]
EXPLORATORY = [("C", "A"), ("D", "B")]

# measure name -> (value of one scored record, or None to leave it out; higher is worse?)
MEASURES = {
    "wrong_figure": (lambda r: float(r.final.has_incorrect), True),
    "wrong_figure_before_verifier": (lambda r: float(r.proposed.has_incorrect), True),
    "wrong_claim_rate": (lambda r: r.final.n_incorrect / r.final.n_claims if r.final.n_claims else None, True),
    "coverage": (lambda r: r.final.coverage, False),
    "acceptable_action": (lambda r: float(bool(r.action_acceptable)), False),
    "insufficient_evidence": (lambda r: float(r.insufficient_evidence), None),
}


def per_case(repeats: list[list[RecordScore]], measure: str, failed_as_wrong: bool = False
             ) -> dict[str, dict[str, float]]:
    """{condition: {case_id: mean over repeats}}. Failed runs are left out unless counted as wrong."""
    fn = MEASURES[measure][0]
    acc: dict[tuple[str, str], list[float]] = {}
    for rows in repeats:
        for r in rows:
            if r.scored:
                v = fn(r)
            elif failed_as_wrong and r.reason == "run_error" and measure == "wrong_figure":
                v = 1.0
            else:
                v = None
            if v is not None:
                acc.setdefault((r.condition, r.case_id), []).append(v)
    out: dict[str, dict[str, float]] = {}
    for (cond, case), vals in acc.items():
        out.setdefault(cond, {})[case] = mean(vals)
    return out


def _bootstrap_ci(diffs: list[float], n_boot: int = N_BOOT, seed: int = SEED) -> tuple[float, float]:
    rng = random.Random(seed)
    n = len(diffs)
    means = sorted(mean(rng.choices(diffs, k=n)) for _ in range(n_boot))
    return means[int(0.025 * n_boot)], means[int(0.975 * n_boot) - 1]


def _wilcoxon_p(diffs: list[float]) -> float | None:
    if not diffs:
        return None
    if all(d == 0 for d in diffs):
        return 1.0
    return float(wilcoxon(diffs, zero_method="wilcox", alternative="two-sided").pvalue)


def compare(values: dict[str, dict[str, float]], a: str, b: str) -> dict:
    """a - b, paired by case (only cases present in both)."""
    cases = sorted(set(values.get(a, {})) & set(values.get(b, {})))
    diffs = [values[a][c] - values[b][c] for c in cases]
    res = {"comparison": f"{a} - {b}", "n_cases": len(cases),
           "mean_" + a: mean(values[a][c] for c in cases) if cases else None,
           "mean_" + b: mean(values[b][c] for c in cases) if cases else None,
           "mean_difference": mean(diffs) if diffs else None, "ci95": None, "p_wilcoxon": _wilcoxon_p(diffs)}
    if len(diffs) >= 2:
        res["ci95"] = _bootstrap_ci(diffs)
    return res


def interaction(values: dict[str, dict[str, float]]) -> dict:
    """(B - A) - (D - C): does the verifier help the single agent and the team differently?"""
    conds = ("A", "B", "C", "D")
    cases = sorted(set.intersection(*(set(values.get(c, {})) for c in conds))) if all(c in values for c in conds) else []
    diffs = [(values["B"][c] - values["A"][c]) - (values["D"][c] - values["C"][c]) for c in cases]
    return {"comparison": "(B - A) - (D - C)", "n_cases": len(cases), "mean_difference": mean(diffs) if diffs else None,
            "ci95": _bootstrap_ci(diffs) if len(diffs) >= 2 else None, "p_wilcoxon": _wilcoxon_p(diffs)}


def holm(ps: list[float | None]) -> list[float | None]:
    order = sorted((p, i) for i, p in enumerate(ps) if p is not None)
    out: list[float | None] = [None] * len(ps)
    running, m = 0.0, len(order)
    for k, (p, i) in enumerate(order):
        running = max(running, min(1.0, (m - k) * p))
        out[i] = running
    return out


def mcnemar_majority(repeats: list[list[RecordScore]], a: str, b: str) -> dict:
    """Exact McNemar on each case's majority outcome (wrong figure in most repeats)."""
    vals = per_case(repeats, "wrong_figure")
    cases = sorted(set(vals.get(a, {})) & set(vals.get(b, {})))
    maj = {c: (vals[a][c] > 0.5, vals[b][c] > 0.5) for c in cases}
    only_a = sum(x and not y for x, y in maj.values())
    only_b = sum(y and not x for x, y in maj.values())
    p = binomtest(only_a, only_a + only_b, 0.5).pvalue if only_a + only_b else 1.0
    return {"comparison": f"{a} vs {b}", "n_cases": len(cases), f"only_{a}_wrong": only_a, f"only_{b}_wrong": only_b,
            "p_exact": float(p)}


def repeatability(repeats: list[list[RecordScore]]) -> dict[str, dict]:
    """Per condition: cases with 2+ scored repeats, and the share whose repeats disagree on a wrong figure."""
    seen: dict[tuple[str, str], set[bool]] = {}
    for rows in repeats:
        for r in rows:
            if r.scored:
                seen.setdefault((r.condition, r.case_id), set()).add(r.final.has_incorrect)
    out = {}
    for cond in sorted({c for c, _ in seen}):
        outcomes = [v for (c, _), v in seen.items() if c == cond]
        out[cond] = {"cases": len(outcomes), "disagree": sum(len(v) > 1 for v in outcomes)}
    return out


def analyse(repeats: list[list[RecordScore]]) -> dict:
    result = {"repeats": len(repeats), "measures": {}}
    for name in MEASURES:
        vals = per_case(repeats, name)
        prim = [compare(vals, a, b) for a, b in PRIMARY]
        for r, p in zip(prim, holm([r["p_wilcoxon"] for r in prim])):
            r["p_holm"] = p
        result["measures"][name] = {
            "per_condition_mean": {c: mean(v.values()) for c, v in sorted(vals.items()) if v},
            "primary": prim,
            "exploratory": [compare(vals, a, b) for a, b in EXPLORATORY] + [interaction(vals)],
        }
    failed = per_case(repeats, "wrong_figure", failed_as_wrong=True)
    result["sensitivity"] = {
        "failed_runs_as_wrong": [compare(failed, a, b) for a, b in PRIMARY],
        "mcnemar_majority": [mcnemar_majority(repeats, a, b) for a, b in PRIMARY],
    }
    result["run_errors"] = {}
    for rows in repeats:
        for r in rows:
            result["run_errors"].setdefault(r.condition, 0)
            result["run_errors"][r.condition] += r.reason == "run_error"
    result["repeatability"] = repeatability(repeats)
    return result


def _f(v, pct=True) -> str:
    if v is None:
        return "n/a"
    return f"{v:+.1%}" if pct else f"{v:.3f}"


def markdown(result: dict) -> str:
    lines = [f"Repeats: {result['repeats']}", ""]
    for name, m in result["measures"].items():
        means = " | ".join(f"{c} {v:.1%}" for c, v in m["per_condition_mean"].items())
        lines += [f"### {name}", f"Per-case mean: {means}", "",
                  "| Comparison | Cases | Mean difference | 95% CI | p (Wilcoxon) | p (Holm) |", "|---|---|---|---|---|---|"]
        for r in m["primary"] + m["exploratory"]:
            ci = f"{r['ci95'][0]:+.1%} to {r['ci95'][1]:+.1%}" if r.get("ci95") else "n/a"
            lines.append(f"| {r['comparison']} | {r['n_cases']} | {_f(r['mean_difference'])} | {ci} | "
                         f"{_f(r['p_wilcoxon'], False)} | {_f(r.get('p_holm'), False) if 'p_holm' in r else '–'} |")
        lines.append("")
    lines.append("### Sensitivity")
    for r in result["sensitivity"]["failed_runs_as_wrong"]:
        lines.append(f"- failed runs as wrong, {r['comparison']}: {_f(r['mean_difference'])}, "
                     f"p = {_f(r['p_wilcoxon'], False)}")
    for r in result["sensitivity"]["mcnemar_majority"]:
        lines.append(f"- McNemar on majority outcome, {r['comparison']}: p = {r['p_exact']:.3f} ({r})")
    for tol, rs in result.get("tolerance", {}).items():
        for r in rs:
            lines.append(f"- tolerance {tol}, {r['comparison']}: {_f(r['mean_difference'])}, "
                         f"p = {_f(r['p_wilcoxon'], False)}")
    lines += ["", f"Run errors per condition: {result['run_errors']}",
              f"Repeats disagreeing on a wrong figure: {result['repeatability']}"]
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("run_dirs", type=Path, nargs="+", help="one folder per repeat")
    ap.add_argument("--references", type=Path, required=True)
    ap.add_argument("--cases", type=Path, required=True)
    ap.add_argument("--rel-tol", type=float, default=SCORE_REL_TOL)
    ap.add_argument("--sensitivity-tols", type=float, nargs="*", default=[0.0005, 0.02])
    ap.add_argument("--out", type=Path)
    a = ap.parse_args(argv)

    refs = load_references(a.references)
    cases = {c.case_id: c for c in (Case.model_validate_json(f.read_text(encoding="utf-8"))
                                    for f in sorted(a.cases.glob("*.json")))}
    def scored(tol):
        return [score_run(d, refs, tol, cases) for d in a.run_dirs]
    result = analyse(scored(a.rel_tol))
    result["rel_tol"] = a.rel_tol
    result["tolerance"] = {str(t): [compare(per_case(scored(t), "wrong_figure"), x, y) for x, y in PRIMARY]
                           for t in a.sensitivity_tols}
    text = markdown(result)
    print(text)
    if a.out:
        a.out.write_text(json.dumps(result, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
