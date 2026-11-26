"""Shared data types. Terms follow GLOSSARY.md.

Money is in one currency per case (EGP by default). Share counts are whole
numbers and never negative: the investor cannot hold a short position.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Literal

import ast
import json
import re

from pydantic import BaseModel, ConfigDict, Field, field_validator


class _Strict(BaseModel):
    model_config = ConfigDict(allow_inf_nan=False, extra="forbid")


# --------------------------------------------------------------------------
# Investor and portfolio
# --------------------------------------------------------------------------


class InvestorProfile(_Strict):
    """Goals, horizon, liquidity needs, willingness and ability to accept losses."""

    goal: str
    horizon: str = Field(description="When the investor expects to need the money, e.g. '3-5 years'")
    liquidity_needs: str
    loss_willingness: Literal["low", "medium", "high"]
    loss_capacity: Literal["low", "medium", "high"]
    language: Literal["en", "ar"] = "en"


class Holding(_Strict):
    ticker: str
    shares: int = Field(ge=0)


class Portfolio(_Strict):
    """Current Portfolio: holdings and cash at a stated time."""

    cash: float = Field(ge=0)
    currency: str = "EGP"
    holdings: list[Holding] = Field(default_factory=list)

    def shares_of(self, ticker: str) -> int:
        return sum(h.shares for h in self.holdings if h.ticker.upper() == ticker.upper())


# --------------------------------------------------------------------------
# Financial evidence
# --------------------------------------------------------------------------


class EvidenceStatus(StrEnum):
    VERIFIED = "verified"    # Verified Financial Figure
    AMBIGUOUS = "ambiguous"  # Ambiguous Financial Figure: must not be used in calculations


class EvidenceItem(_Strict):
    """One Source Value from an official disclosure, with its context."""

    evidence_id: str
    company: str
    document: str
    page: int | None = None
    label: str = Field(description="What the figure is, e.g. 'Net profit attributable to shareholders'")
    source_text: str = Field(description="The value as printed, with surrounding context")
    columns: str | None = Field(default=None, description="The table's column headings as printed, in the order "
                                                          "of the row's numbers, e.g. 'Note | 31/12/2025 | 31/12/2024'")
    value: float | None = Field(default=None, description="Interpreted value in base units; None if unresolved")
    scale: float = Field(default=1.0, description="Multiplier already applied, e.g. 1e6 for 'EGP millions'")
    currency: str | None = "EGP"
    period: str | None = Field(default=None, description="e.g. 'FY2024' or '9M2025 cumulative'")
    status: EvidenceStatus = EvidenceStatus.VERIFIED
    note: str | None = Field(default=None, description="Why a figure is ambiguous, if it is")


# --------------------------------------------------------------------------
# Recommendation (the agent's output)
# --------------------------------------------------------------------------


class Action(StrEnum):
    BUY = "buy"
    HOLD = "hold"
    SELL = "sell"  # reduce or sell an existing holding
    KEEP_CASH = "keep_cash"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"


TRADE_ACTIONS = {Action.BUY, Action.SELL}


class FigureClaim(BaseModel):
    """A financial figure the recommendation relies on, tied to its evidence."""

    evidence_id: str = Field(description="The evidence_id of the figure being cited")
    stated_value: float = Field(description="The number as used in the reasoning, in base units (no scaling)")
    statement: str = Field(description="The sentence in the explanation that uses this figure")


def _decode_list(s: str) -> list | None:
    """Decode list text a model produced, tolerating raw newlines, a stray ']',
    trailing commas and Python quoting. Returns None unless the result is a list."""
    candidates = [s]
    while candidates[-1].endswith("]]") and candidates[-1].count("]") > candidates[-1].count("["):
        candidates.append(candidates[-1][:-1])
    for c in list(candidates):
        candidates.append(re.sub(r",\s*([\]}])", r"\1", c))
    for c in candidates:
        for parse in (lambda t: json.loads(t, strict=False), ast.literal_eval):
            try:
                out = parse(c)
            except (ValueError, SyntaxError, TypeError, MemoryError, RecursionError):
                continue
            if isinstance(out, list):
                return out
    return None


class Recommendation(BaseModel):
    action: Action
    ticker: str | None = Field(default=None, description="Company acted on; required for buy/sell/hold")
    shares: int = Field(default=0, ge=0, description="Shares to buy or sell; 0 for hold/keep_cash/insufficient_evidence")
    explanation: str = Field(description="Why this action, evidence, limitations and portfolio effect")
    claims: list[FigureClaim] = Field(default_factory=list)
    unused_figures: list[str] = Field(
        default_factory=list,
        description="evidence_ids of figures deliberately not used (e.g. ambiguous), with their effect stated in the explanation",
    )
    limitations: list[str] = Field(default_factory=list)

    @field_validator("claims", "unused_figures", "limitations", mode="before")
    @classmethod
    def _decode_list_text(cls, v):
        """Some models send a list as JSON text ('["a", "b"]'); decode it. A lone sentence becomes [sentence]."""
        if isinstance(v, str):
            s = v.strip()
            if s.startswith("["):
                decoded = _decode_list(s)
                return v if decoded is None else decoded  # undecodable: let validation report it
            return [s] if s else []
        return v


# --------------------------------------------------------------------------
# A test case and an experimental condition
# --------------------------------------------------------------------------


class Case(_Strict):
    """One frozen scenario: investor, portfolio, market prices and evidence at an information cutoff."""

    case_id: str
    information_cutoff: str
    profile: InvestorProfile
    portfolio: Portfolio
    prices: dict[str, float] = Field(description="Price per share at the cutoff, by ticker")
    evidence: list[EvidenceItem]
    question: str = "What should I do with my portfolio given this information?"


class Condition(_Strict):
    name: Literal["A", "B", "C", "D"]
    multi_agent: bool
    verifier: bool


CONDITIONS = {
    "A": Condition(name="A", multi_agent=False, verifier=False),
    "B": Condition(name="B", multi_agent=False, verifier=True),
    "C": Condition(name="C", multi_agent=True, verifier=False),
    "D": Condition(name="D", multi_agent=True, verifier=True),
}
