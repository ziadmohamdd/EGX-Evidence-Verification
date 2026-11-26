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


def test_concentrated_buy_is_kept_and_flagged_in_the_record(case, tmp_path):
    # 20,000 cash + 200 SYNA at 50 = 30,000; buying 200 more leaves SYNA at 20,000 (66.7%)
    run_dir = run([case], ["A"], ScriptedModel(script=[buy(shares=200)]), tmp_path, {"provider": "scripted"},
                  fee_rate=0.0)
    rec = json.loads((run_dir / "A" / "synthetic_001.json").read_text(encoding="utf-8"))
    assert rec["status"] == "ok" and not rec["blocked"] and rec["final"]["shares"] == 200
    assert rec["violations"] == [] and [w["rule"] for w in rec["warnings"]] == ["concentration"]


def test_buy_at_half_has_no_warning(case, tmp_path):
    run_dir = run([case], ["A"], ScriptedModel(script=[buy()]), tmp_path, {"provider": "scripted"}, fee_rate=0.0)
    assert json.loads((run_dir / "A" / "synthetic_001.json").read_text(encoding="utf-8"))["warnings"] == []


def test_prompt_marks_ambiguous_evidence(case):
    llm = ScriptedModel(script=[buy()])
    run_case(case, CONDITIONS["A"], llm)
    prompt = llm.seen[0][-1].content
    assert "AMBIGUOUS" in prompt and "SYNB-FY24-rev" in prompt


@pytest.mark.parametrize("name", ["A", "B", "C", "D"])
def test_deciding_prompts_carry_the_one_stock_limit(case, name):
    # the limit matches the scorer's concentration measure (CONCENTRATION_LIMIT = 0.5)
    llm = ScriptedModel(script=[buy()])
    run_case(case, CONDITIONS[name], llm)
    deciding = llm.seen[-1][0].content  # system prompt of the call that made the recommendation
    assert "no single company may be more than half of the portfolio" in deciding
    assert "no exceptions" in deciding
    # hold/keep_cash/insufficient_evidence with a share count is blocked by the portfolio check
    assert "For hold, keep_cash and insufficient_evidence set `shares` to 0" in deciding


def test_printed_view_hides_converted_values(case):
    from egx_guide.agents import render_case
    converted, printed = render_case(case), render_case(case, "printed")
    assert "1.25e+09" in converted and "1.25e+09" not in printed and "value " not in printed
    assert "Net profit 1,250 (EGP millions)" in printed and "Apply the" in printed
    assert "AMBIGUOUS" in printed  # status still shown
    with pytest.raises(ValueError):
        render_case(case, "raw")


@pytest.mark.parametrize("name", ["A", "B", "C", "D"])
def test_printed_view_reaches_every_prompt(case, name):
    llm = ScriptedModel(script=[buy(value=1250), buy()])  # B and D revise once
    run_case(case, CONDITIONS[name], llm, view="printed")
    prompts = [m[-1].content for m in llm.seen]
    assert prompts and all("as printed:" in p for p in prompts)
    assert "1.25e+09" not in prompts[0]  # only the verifier's feedback may quote the converted value


def test_runner_records_evidence_view(case, tmp_path):
    run_dir = run([case], ["A"], ScriptedModel(script=[buy()]), tmp_path, {"provider": "scripted"},
                  fee_rate=0.0, view="printed")
    assert json.loads((run_dir / "manifest.json").read_text())["evidence_view"] == "printed"


def test_resume_keeps_ok_answers_and_reruns_failed_ones(case, tmp_path):
    info = {"provider": "scripted"}
    run_dir = run([case], ["A", "B"], ScriptedModel(script=[buy()]), tmp_path, info, fee_rate=0.0)
    first_a = (run_dir / "A" / "synthetic_001.json").read_text(encoding="utf-8")
    llm = ScriptedModel(script=[buy(shares=50)])  # one answer: only B (the failed one) may use it
    assert run([case], ["A", "B"], llm, tmp_path, info, fee_rate=0.0, resume=run_dir) == run_dir
    assert (run_dir / "A" / "synthetic_001.json").read_text(encoding="utf-8") == first_a
    b = json.loads((run_dir / "B" / "synthetic_001.json").read_text(encoding="utf-8"))
    assert b["status"] == "ok" and b["final"]["shares"] == 50
    assert len(json.loads((run_dir / "manifest.json").read_text())["resumed"]) == 1


def test_resume_adds_conditions_and_refuses_a_different_model(case, tmp_path):
    run_dir = tmp_path / "shared"
    run([case], ["A"], ScriptedModel(script=[buy()]), tmp_path, {"provider": "scripted"}, 0.0, resume=run_dir)
    run([case], ["C"], ScriptedModel(script=[buy()]), tmp_path, {"provider": "scripted"}, 0.0, resume=run_dir)
    assert json.loads((run_dir / "manifest.json").read_text())["conditions"] == ["A", "C"]
    with pytest.raises(SystemExit, match="differ"):
        run([case], ["B"], ScriptedModel(script=[buy()]), tmp_path, {"provider": "other"}, 0.0, resume=run_dir)
