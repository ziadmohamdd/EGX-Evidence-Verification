"""The workflow for one condition, as a LangGraph graph.

    [analysts (multi only)] -> decide -> [verify + one revision (B, D only)] -> portfolio checks -> finalize

Portfolio checks run in every condition. A recommendation that fails them is
blocked: the final output is "insufficient_evidence" with the reason, and the
original is kept in the record for scoring.
"""

from __future__ import annotations

from typing import Any, TypedDict

from langgraph.graph import END, START, StateGraph

from . import agents
from .checks import CheckResult, check_recommendation
from .llm import Caller
from .models import Action, Case, Condition, Recommendation
from .verifier import VerifierReport, run_verifier


class State(TypedDict, total=False):
    case: Case
    reports: dict[str, str]
    proposed: Recommendation        # first decision, before any verifier change
    verified: Recommendation        # after the verifier (same as proposed when it is off)
    verifier_report: VerifierReport | None
    check: CheckResult
    final: Recommendation
    blocked: bool


def build_graph(condition: Condition, caller: Caller, fee_rate: float = 0.0,
                view: agents.EvidenceView = "converted"):
    role = "decision_agent" if condition.multi_agent else "single_agent"

    def analysts(s: State) -> State:
        return {"reports": agents.multi_agent_reports(caller, s["case"], view)}

    def decide(s: State) -> State:
        if condition.multi_agent:
            rec = agents.multi_agent_decide(caller, s["case"], s["reports"], view)
        else:
            rec = agents.single_agent_decide(caller, s["case"], view)
        return {"proposed": rec, "verified": rec, "verifier_report": None}

    def verify(s: State) -> State:
        rec, report = run_verifier(
            s["proposed"], s["case"].evidence,
            revise=lambda r, fb: agents.revise(caller, s["case"], r, fb, role, view))
        return {"verified": rec, "verifier_report": report}

    def check(s: State) -> State:
        c = s["case"]
        return {"check": check_recommendation(s["verified"], c.portfolio, c.prices, fee_rate)}

    def finalize(s: State) -> State:
        result, rec = s["check"], s["verified"]
        if result.ok:
            return {"final": rec, "blocked": False}
        reasons = "; ".join(v.detail for v in result.violations)
        return {"blocked": True, "final": Recommendation(
            action=Action.INSUFFICIENT_EVIDENCE,
            explanation=f"The proposed {rec.action.value} was blocked by the portfolio checks ({reasons}). "
                        "No change to the portfolio is recommended.",
            limitations=[f"Blocked recommendation: {rec.action.value} {rec.shares} {rec.ticker or ''}".strip()],
        )}

    g = StateGraph(State)
    g.add_node("decide", decide)
    g.add_node("check", check)
    g.add_node("finalize", finalize)
    if condition.multi_agent:
        g.add_node("analysts", analysts)
        g.add_edge(START, "analysts")
        g.add_edge("analysts", "decide")
    else:
        g.add_edge(START, "decide")
    if condition.verifier:
        g.add_node("verify", verify)
        g.add_edge("decide", "verify")
        g.add_edge("verify", "check")
    else:
        g.add_edge("decide", "check")
    g.add_edge("check", "finalize")
    g.add_edge("finalize", END)
    return g.compile()


def run_case(case: Case, condition: Condition, llm: Any, fee_rate: float = 0.0,
             view: agents.EvidenceView = "converted") -> tuple[State, Caller]:
    """Run one case under one condition with a fresh graph and no shared memory."""
    caller = Caller(llm)
    state = build_graph(condition, caller, fee_rate, view).invoke({"case": case})
    return state, caller
