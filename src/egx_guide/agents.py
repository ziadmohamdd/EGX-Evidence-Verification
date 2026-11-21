"""Agent prompts and roles.

Single agent: one model call reads everything and decides.
Multi agent: a financial analyst and an investor/portfolio analyst write
reports, then a decision agent decides. Every agent sees the same frozen case,
so the conditions differ only in how the work is split.

Prompts are development drafts. Freeze them before final test runs.
"""

from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage

from .llm import Caller
from .models import Case, Recommendation

LANGUAGE = {"en": "English", "ar": "Arabic"}

RULES = """Rules:
- Use only the evidence and prices given. Do not use outside knowledge about these companies or later events.
- Valid actions: buy, hold, sell (reduce an existing holding), keep_cash, insufficient_evidence.
- Never sell shares the investor does not own or more than they hold. A buy must fit the available cash.
- Every financial figure you rely on must appear in `claims` with its evidence_id and the value in base units (not millions).
- Figures marked AMBIGUOUS must not be used in calculations. List them in `unused_figures` and say in the explanation which conclusions are affected.
- If the evidence is not enough for a responsible decision, choose insufficient_evidence and say what is missing.
- This is guidance, not a guarantee of returns. State uncertainty and risks honestly."""


def render_case(case: Case) -> str:
    p, b = case.profile, case.portfolio
    held = ", ".join(f"{h.ticker}: {h.shares} shares" for h in b.holdings) or "none"
    prices = ", ".join(f"{t}: {v:,.2f} {b.currency}" for t, v in case.prices.items())
    ev = []
    for e in case.evidence:
        status = "AMBIGUOUS" if e.status == "ambiguous" else "verified"
        value = "unresolved" if e.value is None else f"{e.value:,.6g}"
        note = f" | note: {e.note}" if e.note else ""
        ev.append(f"- [{e.evidence_id}] {e.company} | {e.label} | period {e.period} | value {value} "
                  f"{e.currency or ''} | {status} | source: \"{e.source_text}\" ({e.document}, p.{e.page}){note}")
    return f"""Information cutoff: {case.information_cutoff}

Investor profile:
- Goal: {p.goal}
- Horizon: {p.horizon}
- Liquidity needs: {p.liquidity_needs}
- Willingness to accept losses: {p.loss_willingness}; financial ability to withstand losses: {p.loss_capacity}

Current portfolio:
- Cash: {b.cash:,.2f} {b.currency}
- Holdings: {held}

Prices per share at the cutoff: {prices}

Evidence:
{chr(10).join(ev)}

Investor question: {case.question}"""


def _lang(case: Case) -> str:
    return f"Write the explanation in {LANGUAGE[case.profile.language]}."


# ---------------------------------------------------------------- single agent

SINGLE_SYSTEM = f"""You are an investment guide for individual investors in Egyptian listed companies.
Analyse the company evidence and the investor's situation, then give one recommendation.
{RULES}"""


def single_agent_decide(caller: Caller, case: Case) -> Recommendation:
    return caller.structured("single_agent", [
        SystemMessage(SINGLE_SYSTEM),
        HumanMessage(f"{render_case(case)}\n\n{_lang(case)}"),
    ], Recommendation)


# ----------------------------------------------------------------- multi agent

FINANCIAL_SYSTEM = """You are the financial analyst on an investment team covering Egyptian listed companies.
Analyse the company evidence only: profitability, growth, balance sheet, risks, and data quality.
Cite every figure as [evidence_id] with its value. Flag AMBIGUOUS figures and do not compute with them.
Do not recommend an action; the decision agent does that. Use only the evidence given."""

INVESTOR_SYSTEM = """You are the investor-suitability analyst on an investment team.
Assess what suits this investor: horizon, liquidity needs, loss willingness and capacity, current
concentration, and how much cash could reasonably be committed. Note what the portfolio allows
(what can be sold, what cash is free). Do not analyse company financials and do not pick an action."""

DECISION_SYSTEM = f"""You are the decision agent on an investment team for Egyptian listed companies.
Read the financial analyst's and the suitability analyst's reports and the case, then give one recommendation.
Check the analysts' figures against the evidence list; the evidence list is authoritative.
{RULES}"""


def multi_agent_reports(caller: Caller, case: Case) -> dict[str, str]:
    ctx = render_case(case)
    return {
        "financial": caller.text("financial_analyst", [SystemMessage(FINANCIAL_SYSTEM), HumanMessage(ctx)]),
        "investor": caller.text("investor_analyst", [SystemMessage(INVESTOR_SYSTEM), HumanMessage(ctx)]),
    }


def multi_agent_decide(caller: Caller, case: Case, reports: dict[str, str]) -> Recommendation:
    return caller.structured("decision_agent", [
        SystemMessage(DECISION_SYSTEM),
        HumanMessage(f"{render_case(case)}\n\nFinancial analyst report:\n{reports['financial']}\n\n"
                     f"Suitability analyst report:\n{reports['investor']}\n\n{_lang(case)}"),
    ], Recommendation)


# -------------------------------------------------------------- revision (B, D)


def revise(caller: Caller, case: Case, rec: Recommendation, feedback: str, role: str) -> Recommendation:
    system = DECISION_SYSTEM if role == "decision_agent" else SINGLE_SYSTEM
    return caller.structured(f"{role}_revision", [
        SystemMessage(system),
        HumanMessage(f"{render_case(case)}\n\nYour previous recommendation:\n{rec.model_dump_json(indent=2)}\n\n"
                     f"{feedback}\n\n{_lang(case)}"),
    ], Recommendation)
