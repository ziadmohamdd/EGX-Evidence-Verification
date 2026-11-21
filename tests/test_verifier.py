from egx_guide.models import Action, EvidenceItem, EvidenceStatus, FigureClaim, Recommendation
from egx_guide.verifier import REMOVED, check_claims, run_verifier

EVIDENCE = [
    EvidenceItem(evidence_id="e1", company="COMI", document="FY2024.pdf", page=3,
                 label="Net profit", source_text="Net profit 55,123 (EGP millions)",
                 value=55_123e6, scale=1e6, period="FY2024"),
    EvidenceItem(evidence_id="e2", company="COMI", document="FY2024.pdf", page=4,
                 label="Total deposits", source_text="Deposits 1,2?4,000 (smudged)",
                 value=None, status=EvidenceStatus.AMBIGUOUS, note="illegible digit"),
]
STORE = {e.evidence_id: e for e in EVIDENCE}


def claim(eid, value, text="s"):
    return FigureClaim(evidence_id=eid, stated_value=value, statement=text)


def rec_with(*claims, explanation="x"):
    return Recommendation(action=Action.KEEP_CASH, explanation=explanation, claims=list(claims))


def rules(failures):
    return [f.rule for f in failures]


def test_correct_and_rounded_values_pass():
    assert check_claims([claim("e1", 55_123e6), claim("e1", 55.1e9)], STORE) == []


def test_scale_error_is_caught_with_hint():
    [f] = check_claims([claim("e1", 55_123)], STORE)
    assert f.rule == "value_mismatch" and "scale" in f.detail


def test_ambiguous_and_unknown_are_caught():
    assert rules(check_claims([claim("e2", 1), claim("e9", 1)], STORE)) == ["ambiguous_used", "unknown_evidence"]


def test_clean_recommendation_is_not_revised():
    r = rec_with(claim("e1", 55_123e6))
    out, report = run_verifier(r, EVIDENCE, revise=lambda *_: (_ for _ in ()).throw(AssertionError))
    assert out == r and not report.revised


def test_successful_revision_is_kept():
    bad = rec_with(claim("e1", 55_123))
    good = rec_with(claim("e1", 55_123e6))
    seen = []
    out, report = run_verifier(bad, EVIDENCE, revise=lambda r, fb: seen.append(fb) or good)
    assert out == good and report.revised and report.after_revision == []
    assert "e1" in seen[0]


def test_failed_revision_drops_and_discloses():
    sentence = "Deposits grew to 1.2 trillion."
    bad = rec_with(claim("e1", 55_123e6, "ok"), claim("e2", 1.2e12, sentence),
                   explanation=f"Profit is strong. {sentence}")
    out, report = run_verifier(bad, EVIDENCE, revise=lambda r, fb: r)
    assert report.dropped == ["e2"]
    assert [c.evidence_id for c in out.claims] == ["e1"]
    assert out.unused_figures == ["e2"]
    assert sentence not in out.explanation and REMOVED in out.explanation
    assert "Total deposits" in out.limitations[-1]
