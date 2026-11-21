"""All four conditions end to end with a scripted model: no network, no API key."""

import json
from pathlib import Path

import pytest
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.runnables import RunnableLambda
from pydantic import Field

from egx_guide.models import CONDITIONS, Action, FigureClaim, Recommendation
from egx_guide.pipeline import run_case
from egx_guide.runner import load_cases, run

CASES = Path(__file__).parent / "fixtures" / "cases"


class ScriptedModel(BaseChatModel):
    """Text calls return a fixed report; structured calls pop the next scripted Recommendation."""

    script: list = Field(default_factory=list)
    seen: list = Field(default_factory=list)

    @property
    def _llm_type(self) -> str:
        return "scripted"

    def _generate(self, messages, stop=None, run_manager=None, **kwargs) -> ChatResult:
        self.seen.append(messages)
        msg = AIMessage("analyst report", usage_metadata={"input_tokens": 10, "output_tokens": 5, "total_tokens": 15})
        return ChatResult(generations=[ChatGeneration(message=msg)])

    def with_structured_output(self, schema, include_raw=False, **kwargs):
        def answer(messages):
            self.seen.append(messages)
            parsed = self.script.pop(0)
            raw = AIMessage("{}", usage_metadata={"input_tokens": 20, "output_tokens": 8, "total_tokens": 28})
            return {"raw": raw, "parsed": parsed, "parsing_error": None} if include_raw else parsed
        return RunnableLambda(answer)


def buy(shares=100, value=1.25e9):
    return Recommendation(
        action=Action.BUY, ticker="SYNA", shares=shares,
        explanation="Profit was 1.25 billion. Buy more.",
        claims=[FigureClaim(evidence_id="SYNA-FY24-np", stated_value=value, statement="Profit was 1.25 billion.")])


@pytest.fixture
def case():
    return load_cases(CASES)[0]


@pytest.mark.parametrize("name", ["A", "B", "C", "D"])
def test_clean_buy_passes_every_condition(case, name):
    llm = ScriptedModel(script=[buy()])
    state, caller = run_case(case, CONDITIONS[name], llm)
    assert not state["blocked"]
    assert state["final"].action is Action.BUY
    assert state["check"].proposed.cash == 15_000
    roles = [c.role for c in caller.calls]
    expected = ["financial_analyst", "investor_analyst", "decision_agent"] if CONDITIONS[name].multi_agent else ["single_agent"]
    assert roles == expected


def test_verifier_off_lets_wrong_figure_through(case):
    state, _ = run_case(case, CONDITIONS["A"], ScriptedModel(script=[buy(value=1250)]))
    assert state["final"].claims[0].stated_value == 1250  # scale error survives without the verifier
    assert state["verifier_report"] is None


def test_verifier_gets_one_revision_then_drops(case):
    llm = ScriptedModel(script=[buy(value=1250), buy(value=1250)])
    state, caller = run_case(case, CONDITIONS["B"], llm)
    report = state["verifier_report"]
    assert report.revised and report.dropped == ["SYNA-FY24-np"]
    assert state["final"].claims == [] and state["final"].unused_figures == ["SYNA-FY24-np"]
    assert [c.role for c in caller.calls] == ["single_agent", "single_agent_revision"]
    assert "scale error" in llm.seen[-1][-1].content  # feedback reached the model


def test_verifier_revision_fixes_figure(case):
    state, caller = run_case(case, CONDITIONS["D"], ScriptedModel(script=[buy(value=1250), buy()]))
    assert state["verifier_report"].after_revision == []
    assert state["final"].claims[0].stated_value == 1.25e9
    assert caller.calls[-1].role == "decision_agent_revision"


@pytest.mark.parametrize("name", ["A", "B", "C", "D"])
def test_oversell_is_blocked_in_every_condition(case, name):
    oversell = Recommendation(action=Action.SELL, ticker="SYNA", shares=500, explanation="Sell.")
    state, _ = run_case(case, CONDITIONS[name], ScriptedModel(script=[oversell]))
    assert state["blocked"] and state["final"].action is Action.INSUFFICIENT_EVIDENCE
    assert state["proposed"].shares == 500  # original kept for scoring


def test_runner_writes_records_and_keeps_errors(case, tmp_path):
    llm = ScriptedModel(script=[buy()])  # second condition runs out of script -> error record
    run_dir = run([case], ["A", "B"], llm, tmp_path, {"provider": "scripted"}, fee_rate=0.0)
    ok = json.loads((run_dir / "A" / "synthetic_001.json").read_text(encoding="utf-8"))
    err = json.loads((run_dir / "B" / "synthetic_001.json").read_text(encoding="utf-8"))
    assert ok["status"] == "ok" and ok["final"]["action"] == "buy" and ok["calls"][0]["input_tokens"] == 20
    assert err["status"] == "error"
    assert json.loads((run_dir / "manifest.json").read_text())["conditions"] == ["A", "B"]


def test_prompt_marks_ambiguous_evidence(case):
    llm = ScriptedModel(script=[buy()])
    run_case(case, CONDITIONS["A"], llm)
    prompt = llm.seen[0][-1].content
    assert "AMBIGUOUS" in prompt and "SYNB-FY24-rev" in prompt
