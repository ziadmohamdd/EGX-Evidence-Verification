"""The evidence verifier: the experimental intervention (on in B and D, off in A and C).

Each FigureClaim is checked against the frozen evidence, and so is every figure
written in the explanation: a number there that matches an evidence figure must be
cited in `claims`, and a number that matches one only at the wrong scale is a
mismatch. Without the text check an agent could pass by citing nothing while still
stating figures. On failure the agent gets one chance to revise (via ``revise``).
What still fails is removed from the recommendation (claims, and the sentences that
state an unchecked figure), listed as unused figures, and disclosed as a limitation.
Figures cited before the revision but not after are recorded as withdrawn.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass, field

from .models import EvidenceItem, EvidenceStatus, FigureClaim, Recommendation

DEFAULT_REL_TOL = 0.005  # 0.5%: allows rounding in prose, not wrong digits or scale

REMOVED = "[removed: figure could not be verified]"

# Text figures smaller than this (per-share values, ratios) are matched only exactly, so a
# P/E of 11.9 is not mistaken for an EPS of 11.93. Larger amounts are matched within rel_tol.
EXACT_BELOW = 1e6
SCALE_WORDS = {
    "thousand": 1e3, "k": 1e3, "million": 1e6, "mn": 1e6, "m": 1e6,
    "billion": 1e9, "bn": 1e9, "b": 1e9, "trillion": 1e12, "tn": 1e12,
    "ألف": 1e3, "آلاف": 1e3, "مليون": 1e6, "ملايين": 1e6, "مليار": 1e9, "مليارات": 1e9,
}
_TEXT_NUMBER = re.compile(
    r"(?<![\w.,٫٬])(\d[\d,٬]*(?:[.٫]\d+)?(?:[eE][+-]?\d+)?)"
    r"(?:(\s*[%٪])|\s*(" + "|".join(sorted(map(re.escape, SCALE_WORDS), key=len, reverse=True)) + r")(?!\w))?",
    re.IGNORECASE)
# "22,578,063 × 1,000" is the agent showing the unit conversion, not a scale error.
_TIMES_UNIT = re.compile(r"\s*[×xX*]\s*1(?:[,\s]?000){1,3}(?!\d)")
_DIGIT_MAP = str.maketrans({**{chr(0x0660 + i): str(i) for i in range(10)},
                            **{chr(0x06F0 + i): str(i) for i in range(10)}, "٫": ".", "٬": "", ",": ""})


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
    withdrawn: list[str] = field(default_factory=list)  # cited before the revision, not after


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


@dataclass(frozen=True)
class TextFigure:
    raw: str
    value: float
    start: int
    end: int
    whole_digits: int  # digits before the decimal point
    scaled: bool       # written with a scale word ('million', 'bn', 'مليار')


def text_figures(text: str) -> list[TextFigure]:
    """Numbers written in prose, with 'million'/'bn'/'مليون' applied. Percentages are skipped."""
    out = []
    for m in _TEXT_NUMBER.finditer(text):
        if m.group(2):
            continue
        num = m.group(1).translate(_DIGIT_MAP)
        try:
            value = float(num)
        except ValueError:
            continue
        if m.group(3):
            value *= SCALE_WORDS[m.group(3).lower()]
        whole = re.split(r"[.eE]", num)[0]
        out.append(TextFigure(m.group(0), value, m.start(), m.end(), len(whole), bool(m.group(3))))
    return out


def _matches(stated: float, value: float, rel_tol: float) -> bool:
    if abs(value) < EXACT_BELOW:
        return abs(stated - value) < 1e-9
    return abs(stated - value) <= rel_tol * abs(value)


@dataclass(frozen=True)
class TextFinding:
    evidence_id: str
    rule: str          # "uncited_figure" or "text_value_mismatch"
    figure: TextFigure
    value: float       # the evidence (or reference) value it matched
    scale: float | None = None  # for a mismatch: the factor that would make it match


def text_findings(text: str, values: dict[str, float], cited: set[str],
                  rel_tol: float = DEFAULT_REL_TOL) -> list[TextFinding]:
    """Figures in `text` that match one of `values` (by evidence_id) but are not in `cited`,
    or match one only at the wrong scale. Shared by the verifier and the scorer."""
    found = []
    for t in text_figures(text):
        hits = [i for i, v in values.items() if _matches(t.value, v, rel_tol)]
        if hits:
            if not any(i in cited for i in hits):
                found.append(TextFinding(hits[0], "uncited_figure", t, values[hits[0]]))
            continue
        if t.whole_digits < 4 and not t.scaled:
            continue  # short plain numbers (prices like 82.50, share counts) match by chance
        if _TIMES_UNIT.match(text, t.end):
            continue
        for i, v in values.items():
            if abs(v) < EXACT_BELOW:
                continue
            f = next((f for f in (1e3, 1e6, 1e9, 1e-3, 1e-6, 1e-9)
                      if abs(t.value * f - v) <= rel_tol * abs(v)), None)
            if f is not None:
                found.append(TextFinding(i, "text_value_mismatch", t, v, f))
                break
    return found


def check_text(
    rec: Recommendation,
    evidence: dict[str, EvidenceItem],
    rel_tol: float = DEFAULT_REL_TOL,
) -> list[tuple[ClaimFailure, TextFigure]]:
    """Figures in the explanation that match evidence but are not cited, or match only at the wrong scale."""
    values = {e.evidence_id: e.value for e in evidence.values()
              if e.value is not None and e.status is not EvidenceStatus.AMBIGUOUS}
    out = []
    for f in text_findings(rec.explanation, values, {c.evidence_id for c in rec.claims}, rel_tol):
        e, t = evidence[f.evidence_id], f.figure
        if f.rule == "uncited_figure":
            detail = (f"the explanation states \"{t.raw}\", which is '{e.label}' ({e.value:,.6g}), "
                      "but it is not listed in claims")
        else:
            detail = (f"the explanation states \"{t.raw}\" but evidence '{e.label}' is {e.value:,.6g} "
                      f"[{e.source_text}] (looks like a scale error by {f.scale:g})")
        out.append((ClaimFailure(e.evidence_id, f.rule, detail), t))
    return out


_SENTENCE_END = re.compile(r"[.!?؟](?=\s|$)|\n")


def _remove_sentences(text: str, spans: list[tuple[int, int]]) -> str:
    """Replace each sentence containing one of the spans with REMOVED."""
    ranges = set()
    for start, end in spans:
        before = [m.end() for m in _SENTENCE_END.finditer(text, 0, start)]
        s0 = before[-1] if before else 0
        after = _SENTENCE_END.search(text, end)
        ranges.add((s0, after.end() if after else len(text)))
    for s0, s1 in sorted(ranges, reverse=True):
        chunk = text[s0:s1]
        lead = chunk[:len(chunk) - len(chunk.lstrip())]
        text = text[:s0] + lead + REMOVED + text[s1:]
    return text


def feedback_text(failures: list[ClaimFailure]) -> str:
    lines = ["The evidence check found problems with these figures:"]
    lines += [f"- {f.evidence_id}: {f.rule}: {f.detail}" for f in failures]
    lines.append(
        "Revise the recommendation. Correct each figure from the evidence, or stop relying on it, "
        "list it in unused_figures and say in the explanation which conclusions are affected. "
        "Every figure from the evidence that the explanation states must be listed in claims; "
        "removing a figure from claims while still stating it does not fix it. "
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

    def check(r: Recommendation) -> list[ClaimFailure]:
        return check_claims(r.claims, store, rel_tol) + [f for f, _ in check_text(r, store, rel_tol)]

    report = VerifierReport(first_pass=check(rec))
    if not report.first_pass:
        return rec, report

    cited_before = {c.evidence_id for c in rec.claims}
    rec = revise(rec, feedback_text(report.first_pass))
    report.revised = True
    report.withdrawn = sorted(cited_before - {c.evidence_id for c in rec.claims})
    report.after_revision = check(rec)
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
    # Whatever the text still states without a kept claim behind it is removed too.
    left = check_text(rec.model_copy(update={"claims": kept, "explanation": explanation}), store, rel_tol)
    explanation = _remove_sentences(explanation, [(t.start, t.end) for _, t in left])
    bad |= {f.evidence_id for f, _ in left}
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
