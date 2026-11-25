"""Score a run folder against the partner's reference answers.

Usage:
    python -m egx_guide.score runs/<timestamp> --references data/references

Each figure a recommendation cites is judged against the **reference answer**,
not against the evidence store the agents saw. The evidence store can itself
contain extraction errors; the reference answers are the ground truth.

Accuracy and coverage are reported together (PROJECT_AUDIT_SUMMARY.md 6.3), so a
system cannot look precise just by citing nothing. Both the agent's first
recommendation (``proposed``) and the one shown to the investor (``final``)
are scored, so the verifier's effect can be seen directly.

The metric definitions here are a working draft; the paper's primary endpoints
are not locked yet.

Writes ``scores.json`` (every record plus the summary) and ``summary.csv`` into
the run folder and prints a Markdown table.
"""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict, dataclass, field
from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .models import Action

SCORE_REL_TOL = 0.005  # 0.5%: rounding in prose is fine; wrong digits or scale are not


# --------------------------------------------------------------------------
# Reference answers (prepared by one author, checked by the other)
# --------------------------------------------------------------------------


class ReferenceFigure(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)

    value: float | None = Field(description="True value in base units (EGP, not millions); null if unresolvable")
    usable: bool = Field(default=True, description="False if the figure is ambiguous and must not be relied on")
    note: str | None = None

    @model_validator(mode="after")
    def _usable_needs_value(self):
        if self.usable and self.value is None:
            raise ValueError("a usable figure needs a value; mark it usable=false if it cannot be resolved")
        return self


class ReferenceAnswer(BaseModel):
    model_config = ConfigDict(extra="forbid")

    case_id: str
    figures: dict[str, ReferenceFigure] = Field(description="By evidence_id, for every evidence item in the case")
    acceptable_actions: list[Action] = Field(min_length=1)
    prepared_by: str | None = None
    checked_by: str | None = None
    notes: str | None = None


def load_references(folder: Path) -> dict[str, ReferenceAnswer]:
    refs = {}
    for f in sorted(folder.glob("*.json")):
        ref = ReferenceAnswer.model_validate_json(f.read_text(encoding="utf-8"))
        if ref.case_id in refs:
            raise ValueError(f"duplicate reference for {ref.case_id} in {f}")
        refs[ref.case_id] = ref
    return refs


# --------------------------------------------------------------------------
# Scoring one recommendation
# --------------------------------------------------------------------------


class ClaimVerdict(StrEnum):
    CORRECT = "correct"
    WRONG_VALUE = "wrong_value"        # cites a real figure with the wrong number
    AMBIGUOUS_USED = "ambiguous_used"  # relies on a figure the reference says is unusable
    UNKNOWN = "unknown"                # cites an evidence_id that does not exist


@dataclass
class ScoredClaim:
    evidence_id: str
    stated_value: float
    reference_value: float | None
    verdict: ClaimVerdict
    scale_error: float | None = None  # e.g. 1e6 if the agent dropped "millions"


@dataclass
class RecScore:
    claims: list[ScoredClaim]
    usable_reference_figures: int
    covered: int  # distinct usable figures cited correctly

    @property
    def n_claims(self) -> int:
        return len(self.claims)

    @property
    def n_correct(self) -> int:
        return sum(c.verdict is ClaimVerdict.CORRECT for c in self.claims)

    @property
    def n_incorrect(self) -> int:
        return self.n_claims - self.n_correct

    @property
    def claim_precision(self) -> float | None:
        return self.n_correct / self.n_claims if self.claims else None

    @property
    def coverage(self) -> float | None:
        return self.covered / self.usable_reference_figures if self.usable_reference_figures else None

    @property
    def has_incorrect(self) -> bool:
        return self.n_incorrect > 0

    def as_dict(self) -> dict:
        return {
            "n_claims": self.n_claims, "n_correct": self.n_correct, "n_incorrect": self.n_incorrect,
            "claim_precision": self.claim_precision, "coverage": self.coverage,
            "claims": [{**asdict(c), "verdict": c.verdict.value} for c in self.claims],
        }


@dataclass
class RecordScore:
    case_id: str
    condition: str
    scored: bool
    reason: str | None = None  # why not scored
    proposed: RecScore | None = None
    final: RecScore | None = None
    action: str | None = None
    action_acceptable: bool | None = None
    insufficient_evidence: bool = False
    n_violations: int = 0
    blocked: bool = False
    verifier_revised: bool = False
    verifier_dropped: int = 0
    extra: dict = field(default_factory=dict)

    def as_dict(self) -> dict:
        d = {k: v for k, v in asdict(self).items() if k not in ("proposed", "final")}
        d["proposed"] = self.proposed.as_dict() if self.proposed else None
        d["final"] = self.final.as_dict() if self.final else None
        return d


def _close(a: float, b: float, rel_tol: float) -> bool:
    return abs(a - b) <= rel_tol * max(abs(b), 1e-9)


def judge_claim(evidence_id: str, stated: float, ref: ReferenceAnswer, rel_tol: float) -> ScoredClaim:
    fig = ref.figures.get(evidence_id)
    if fig is None:
        return ScoredClaim(evidence_id, stated, None, ClaimVerdict.UNKNOWN)
    if not fig.usable or fig.value is None:
        return ScoredClaim(evidence_id, stated, fig.value, ClaimVerdict.AMBIGUOUS_USED)
    if _close(stated, fig.value, rel_tol):
        return ScoredClaim(evidence_id, stated, fig.value, ClaimVerdict.CORRECT)
    scale = next((f for f in (1e3, 1e6, 1e9, 1e-3, 1e-6, 1e-9) if _close(stated * f, fig.value, rel_tol)), None)
    return ScoredClaim(evidence_id, stated, fig.value, ClaimVerdict.WRONG_VALUE, scale)


def score_recommendation(rec: dict, ref: ReferenceAnswer, rel_tol: float = SCORE_REL_TOL) -> RecScore:
    claims = [judge_claim(c["evidence_id"], float(c["stated_value"]), ref, rel_tol) for c in rec.get("claims", [])]
    usable = {k for k, f in ref.figures.items() if f.usable}
    covered = {c.evidence_id for c in claims if c.verdict is ClaimVerdict.CORRECT} & usable
    return RecScore(claims, len(usable), len(covered))


def score_record(rec: dict, ref: ReferenceAnswer | None, rel_tol: float = SCORE_REL_TOL) -> RecordScore:
    base = RecordScore(case_id=rec["case_id"], condition=rec["condition"], scored=False)
    if rec.get("status") != "ok":
        base.reason = "run_error"
        return base
    if ref is None:
        base.reason = "no_reference"
        return base

    final = rec["final"]
    action = Action(final["action"])
    verifier = rec.get("verifier") or {}
    return RecordScore(
        case_id=rec["case_id"], condition=rec["condition"], scored=True,
        proposed=score_recommendation(rec.get("proposed") or final, ref, rel_tol),
        final=score_recommendation(final, ref, rel_tol),
        action=action.value,
        action_acceptable=action in ref.acceptable_actions,
        insufficient_evidence=action is Action.INSUFFICIENT_EVIDENCE,
        n_violations=len(rec.get("violations") or []),
        blocked=bool(rec.get("blocked")),
        verifier_revised=bool(verifier.get("revised")),
        # figures removed by the verifier, plus figures the agent withdrew in its revision
        verifier_dropped=len(set(verifier.get("dropped") or []) | set(verifier.get("withdrawn") or [])),
    )


# --------------------------------------------------------------------------
# A whole run
# --------------------------------------------------------------------------


def score_run(run_dir: Path, refs: dict[str, ReferenceAnswer], rel_tol: float = SCORE_REL_TOL) -> list[RecordScore]:
    rows = []
    for f in sorted(run_dir.glob("*/*.json")):
        rec = json.loads(f.read_text(encoding="utf-8"))
        rows.append(score_record(rec, refs.get(rec["case_id"]), rel_tol))
    if not rows:
        raise SystemExit(f"no run records under {run_dir}")
    return rows


def _mean(xs: list[float | None]) -> float | None:
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


def _rate(num: int, den: int) -> float | None:
    return num / den if den else None


def summarise(rows: list[RecordScore]) -> list[dict]:
    out = []
    for cond in sorted({r.condition for r in rows}):
        all_ = [r for r in rows if r.condition == cond]
        ok = [r for r in all_ if r.scored]
        claims = sum(r.final.n_claims for r in ok)
        wrong = sum(r.final.n_incorrect for r in ok)
        p_claims = sum(r.proposed.n_claims for r in ok)
        p_wrong = sum(r.proposed.n_incorrect for r in ok)
        out.append({
            "condition": cond,
            "records": len(all_),
            "scored": len(ok),
            "run_errors": sum(r.reason == "run_error" for r in all_),
            "no_reference": sum(r.reason == "no_reference" for r in all_),
            # final recommendation (what the investor sees)
            "claims": claims,
            "incorrect_claims": wrong,
            "incorrect_claim_rate": _rate(wrong, claims),
            "share_with_incorrect_claim": _rate(sum(r.final.has_incorrect for r in ok), len(ok)),
            "wrong_value": sum(c.verdict is ClaimVerdict.WRONG_VALUE for r in ok for c in r.final.claims),
            "ambiguous_used": sum(c.verdict is ClaimVerdict.AMBIGUOUS_USED for r in ok for c in r.final.claims),
            "unknown_evidence": sum(c.verdict is ClaimVerdict.UNKNOWN for r in ok for c in r.final.claims),
            "scale_errors": sum(c.scale_error is not None for r in ok for c in r.final.claims),
            "mean_coverage": _mean([r.final.coverage for r in ok]),
            # before the verifier
            "proposed_incorrect_claim_rate": _rate(p_wrong, p_claims),
            # decision and portfolio
            "action_acceptable_rate": _rate(sum(bool(r.action_acceptable) for r in ok), len(ok)),
            "insufficient_evidence_rate": _rate(sum(r.insufficient_evidence for r in ok), len(ok)),
            "portfolio_violations": sum(r.n_violations for r in ok),
            "blocked": sum(r.blocked for r in ok),
            "verifier_revised": sum(r.verifier_revised for r in ok),
            "verifier_dropped": sum(r.verifier_dropped for r in ok),
        })
    return out


TABLE_COLUMNS = [
    ("condition", "Cond"), ("scored", "Scored"), ("run_errors", "Errors"),
    ("claims", "Claims"), ("incorrect_claim_rate", "Wrong-claim rate"),
    ("proposed_incorrect_claim_rate", "…before verifier"),
    ("share_with_incorrect_claim", "Recs with a wrong claim"), ("mean_coverage", "Coverage"),
    ("action_acceptable_rate", "Acceptable action"), ("portfolio_violations", "Portfolio violations"),
]


def _fmt(v) -> str:
    if v is None:
        return "n/a"
    if isinstance(v, float):
        return f"{v:.1%}"
    return str(v)


def markdown_table(summary: list[dict]) -> str:
    head = "| " + " | ".join(t for _, t in TABLE_COLUMNS) + " |"
    sep = "|" + "|".join("---" for _ in TABLE_COLUMNS) + "|"
    rows = ["| " + " | ".join(_fmt(s[k]) for k, _ in TABLE_COLUMNS) + " |" for s in summary]
    return "\n".join([head, sep, *rows])


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("run_dir", type=Path)
    ap.add_argument("--references", type=Path, required=True)
    ap.add_argument("--rel-tol", type=float, default=SCORE_REL_TOL)
    a = ap.parse_args(argv)

    rows = score_run(a.run_dir, load_references(a.references), a.rel_tol)
    summary = summarise(rows)
    (a.run_dir / "scores.json").write_text(json.dumps({
        "rel_tol": a.rel_tol, "references": str(a.references),
        "summary": summary, "records": [r.as_dict() for r in rows],
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    with (a.run_dir / "summary.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(summary[0]))
        w.writeheader()
        w.writerows(summary)
    print(markdown_table(summary))


if __name__ == "__main__":
    main()
