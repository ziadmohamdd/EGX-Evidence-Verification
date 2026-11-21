"""The evidence verifier: the experimental intervention (on in B and D, off in A and C).

Each FigureClaim is checked against the frozen evidence. On failure the agent
gets one chance to revise (via ``revise``). Claims that still fail are removed
from the recommendation, listed as unused figures, and disclosed as a limitation.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

from .models import EvidenceItem, EvidenceStatus, FigureClaim, Recommendation

DEFAULT_REL_TOL = 0.005  # 0.5%: allows rounding in prose, not wrong digits or scale

REMOVED = "[removed: figure could not be verified]"


@dataclass(frozen=True)
class ClaimFailure:
    evidence_id: str
    rule: str
    detail: str


@dataclass
class VerifierReport:
    first_pass: list[ClaimFailure] = field(default_factory=list)
    revised: bool = False
    after_revision: list[ClaimFailure] = field(default_factory=list)
    dropped: list[str] = field(default_factory=list)


def check_claims(
    claims: list[FigureClaim],
    evidence: dict[str, EvidenceItem],
    rel_tol: float = DEFAULT_REL_TOL,
) -> list[ClaimFailure]:
    failures = []
    for c in claims:
        item = evidence.get(c.evidence_id)
        if item is None:
            failures.append(ClaimFailure(c.evidence_id, "unknown_evidence", "no such evidence_id"))
            continue
        if item.status is EvidenceStatus.AMBIGUOUS or item.value is None:
            failures.append(ClaimFailure(
                c.evidence_id, "ambiguous_used",
                f"'{item.label}' is ambiguous ({item.note or 'unresolved'}) and must not be used"))
            continue
        if abs(c.stated_value - item.value) > rel_tol * max(abs(item.value), 1e-9):
            hint = ""
            for factor in (1e3, 1e6, 1e9):
                for f in (factor, 1 / factor):
                    if abs(c.stated_value * f - item.value) <= rel_tol * abs(item.value):
                        hint = f" (looks like a scale error by {f:g})"
            failures.append(ClaimFailure(
                c.evidence_id, "value_mismatch",
                f"stated {c.stated_value:,.6g} but evidence '{item.label}' is {item.value:,.6g} "
                f"[{item.source_text}]{hint}"))
    return failures


def feedback_text(failures: list[ClaimFailure]) -> str:
    lines = ["The evidence check found problems with these figures:"]
    lines += [f"- {f.evidence_id}: {f.rule}: {f.detail}" for f in failures]
    lines.append(
        "Revise the recommendation. Correct each figure from the evidence, or stop relying on it, "
        "list it in unused_figures and say in the explanation which conclusions are affected. "
        "Do not use ambiguous figures.")
    return "\n".join(lines)


def run_verifier(
    rec: Recommendation,
    evidence: list[EvidenceItem],
    revise: Callable[[Recommendation, str], Recommendation],
    rel_tol: float = DEFAULT_REL_TOL,
) -> tuple[Recommendation, VerifierReport]:
    """Check, allow one revision, then drop what still fails ("fix then flag")."""
    store = {e.evidence_id: e for e in evidence}
    report = VerifierReport(first_pass=check_claims(rec.claims, store, rel_tol))
    if not report.first_pass:
        return rec, report

    rec = revise(rec, feedback_text(report.first_pass))
    report.revised = True
    report.after_revision = check_claims(rec.claims, store, rel_tol)
    if not report.after_revision:
        return rec, report

    bad = {f.evidence_id for f in report.after_revision}
    kept, explanation = [], rec.explanation
    for c in rec.claims:
        if c.evidence_id in bad:
            if c.statement and c.statement in explanation:
                explanation = explanation.replace(c.statement, REMOVED)
        else:
            kept.append(c)
    report.dropped = sorted(bad)
    labels = ", ".join(store[i].label if i in store else i for i in report.dropped)
    rec = rec.model_copy(update={
        "claims": kept,
        "explanation": explanation,
        "unused_figures": sorted(set(rec.unused_figures) | bad),
        "limitations": [*rec.limitations,
                        f"These figures could not be verified and were not used: {labels}. "
                        "Conclusions that depended on them are uncertain."],
    })
    return rec, report
