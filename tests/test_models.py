import pytest
from pydantic import ValidationError

from egx_guide.models import Recommendation


def test_lists_sent_as_json_text_are_decoded():
    # seen 2026-11-22 from a free model: limitations='["..."]' instead of a list
    rec = Recommendation.model_validate({
        "action": "hold", "ticker": "ETEL", "explanation": "x",
        "limitations": '["No net profit figure", "Prices change"]',
        "unused_figures": '[]',
        "claims": '[{"evidence_id": "e1", "stated_value": 1.5, "statement": "s"}]',
    })
    assert rec.limitations == ["No net profit figure", "Prices change"]
    assert rec.unused_figures == [] and rec.claims[0].evidence_id == "e1"


@pytest.mark.parametrize("text, expected", [
    ('["line one\nstill line one", "two"]', ["line one\nstill line one", "two"]),   # raw newline inside a string
    ('["a", "b"]]', ["a", "b"]),                                                    # stray closing bracket
    ("['single', 'quotes']", ["single", "quotes"]),                                 # Python-style list
    ('["trailing comma",]', ["trailing comma"]),
])
def test_slightly_malformed_list_text_is_decoded(text, expected):
    rec = Recommendation(action="hold", ticker="ETEL", explanation="x", limitations=text)
    assert rec.limitations == expected


def test_a_plain_sentence_becomes_a_one_item_list():
    rec = Recommendation(action="hold", ticker="ETEL", explanation="x", limitations="Only one year of data")
    assert rec.limitations == ["Only one year of data"]


def test_real_mistakes_are_still_rejected():
    with pytest.raises(ValidationError):
        Recommendation.model_validate({"action": "hold", "explanation": "x", "claims": '[{"evidence_id": "e1"}]'})
    with pytest.raises(ValidationError):
        Recommendation.model_validate({"action": "moon", "explanation": "x"})
