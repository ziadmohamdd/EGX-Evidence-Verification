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


# ------------------------------------------------- figures written in the explanation

EPS = EvidenceItem(evidence_id="e3", company="COMI", document="FY2024.pdf", page=5, label="EPS",
                   source_text="Earnings per share 4.38", value=4.38, period="FY2024")
STORE3 = {**STORE, "e3": EPS}


def text_rules(rec):
    from egx_guide.verifier import check_text
    return [f.rule for f, _ in check_text(rec, STORE3)]


def test_cited_text_figure_passes_rounded_or_exact():
    for text in ("Profit was 55.1 billion.", "Profit was EGP 55,123,000,000.", "Profit was 55,123 million."):
        assert text_rules(rec_with(claim("e1", 55_123e6), explanation=text)) == []


def test_uncited_text_figure_is_caught_in_english_and_arabic():
    assert text_rules(rec_with(explanation="Profit was 55.1 billion.")) == ["uncited_figure"]
    assert text_rules(rec_with(explanation="بلغ صافي الربح ٥٥٫١ مليار جنيه.")) == ["uncited_figure"]
    assert text_rules(rec_with(explanation="EPS was 4.38 pounds.")) == ["uncited_figure"]
    assert text_rules(rec_with(explanation="Profit rose to 5.5123e10 EGP.")) == ["uncited_figure"]


def test_text_scale_error_is_caught():
    assert text_rules(rec_with(explanation="Net profit was 55,123 pounds.")) == ["text_value_mismatch"]
    assert text_rules(rec_with(explanation="Net profit was 55.1 million.")) == ["text_value_mismatch"]
    assert text_rules(rec_with(explanation="The price is 55.12 EGP.")) == []  # a price, not 55.1 bn
    # showing the conversion is fine; the converted result is what must be cited
    shown = "Profit was 55,123 × 1,000,000 = 55,123,000,000 pounds."
    assert text_rules(rec_with(claim("e1", 55_123e6), explanation=shown)) == []
    for tagged in ["Profit was 55,123 (EGP mn) = 55,123,000,000 pounds.",
                   "Profit was 55,123 L.E. (000,000), i.e. 55,123,000,000 pounds."]:
        assert text_rules(rec_with(claim("e1", 55_123e6), explanation=tagged)) == []
    # a bracket without a unit does not excuse the scale
    assert text_rules(rec_with(explanation="Net profit was 55,123 (approx.) pounds.")) == ["text_value_mismatch"]


def test_percentages_ratios_and_small_numbers_are_not_figures():
    # 55.1% is a percentage; a P/E of 4.4 is not the EPS of 4.38; 2024 and 300 shares match nothing
    text = "Margin was 55.1%. The P/E is 4.4. Buy 300 shares in 2024."
    assert text_rules(rec_with(explanation=text)) == []


def test_citing_nothing_does_not_pass_the_verifier():
    """The loophole: a revision drops every claim but still states the figure in its text."""
    sentence = "Profit reached 55,123,000,000 pounds."
    bad = rec_with(claim("e1", 55_123), explanation=f"Strong year. {sentence} Hold.")
    no_claims = rec_with(explanation=f"Strong year. {sentence} Hold.")
    out, report = run_verifier(bad, EVIDENCE, revise=lambda r, fb: no_claims)
    assert report.revised and report.withdrawn == ["e1"]
    assert [f.rule for f in report.after_revision] == ["uncited_figure"]
    assert report.dropped == ["e1"] and out.unused_figures == ["e1"]
    assert sentence not in out.explanation and REMOVED in out.explanation
    assert out.explanation.startswith("Strong year.") and out.explanation.endswith("Hold.")


def test_dropped_claim_takes_its_text_figure_with_it():
    """The claim's statement is not verbatim in the text, so the figure is found by value."""
    bad = rec_with(claim("e1", 55_123, "profit 55,123"), explanation="Profit was 55.1 billion. Hold.")
    out, report = run_verifier(bad, EVIDENCE, revise=lambda r, fb: r)
    assert report.dropped == ["e1"] and out.claims == []
    assert "55.1 billion" not in out.explanation and out.explanation.endswith("Hold.")


def test_uncited_text_figure_triggers_a_revision_that_can_fix_it():
    uncited = rec_with(explanation="Profit was 55.1 billion.")
    fixed = rec_with(claim("e1", 55_123e6), explanation="Profit was 55.1 billion.")
    seen = []
    out, report = run_verifier(uncited, EVIDENCE, revise=lambda r, fb: seen.append(fb) or fixed)
    assert out == fixed and report.after_revision == [] and report.withdrawn == []
    assert "not listed in claims" in seen[0]
