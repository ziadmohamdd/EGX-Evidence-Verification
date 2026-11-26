"""Mandatory portfolio and arithmetic checks.

Plain code, no language model. These run in every experimental condition and
cannot be talked past: an invalid recommendation is blocked whatever its prose says.

Warnings are different: they flag a valid but unwise recommendation (a buy leaving
more than half the portfolio in one stock) in the record without blocking it, so the
evaluation can see when an agent breaks the prompt's rule.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .models import TRADE_ACTIONS, Action, Holding, Portfolio, Recommendation

CONCENTRATION_LIMIT = 0.5  # a buy leaving more than this share of the portfolio in one stock is flagged


@dataclass(frozen=True)
class Violation:
    rule: str
    detail: str


@dataclass
class CheckResult:
    violations: list[Violation] = field(default_factory=list)
    proposed: Portfolio | None = None  # Proposed Portfolio if the recommendation were followed
    warnings: list[Violation] = field(default_factory=list)  # flagged, not blocking

    @property
    def ok(self) -> bool:
        return not self.violations


def check_recommendation(
    rec: Recommendation,
    portfolio: Portfolio,
    prices: dict[str, float],
    fee_rate: float = 0.0,
) -> CheckResult:
    """Check holdings, cash and share arithmetic, and compute the Proposed Portfolio.

    ``fee_rate`` is the total transaction cost as a fraction of trade value. Its
    real value for EGX is not decided yet; experiments must state the one used.
    """
    v: list[Violation] = []
    ticker = rec.ticker.upper() if rec.ticker else None
    price = prices.get(ticker) if ticker else None

    if rec.action in TRADE_ACTIONS:
        if ticker is None:
            v.append(Violation("ticker_required", f"{rec.action.value} needs a ticker"))
        elif price is None:
            v.append(Violation("unknown_price", f"no price for {ticker} at the cutoff"))
        if rec.shares <= 0:
            v.append(Violation("positive_shares", f"{rec.action.value} needs a positive share count"))
    elif rec.shares != 0:
        v.append(Violation("no_shares_without_trade", f"{rec.action.value} must not carry a share count"))

    if rec.action is Action.HOLD and ticker is not None and portfolio.shares_of(ticker) == 0:
        v.append(Violation("hold_unowned", f"cannot hold {ticker}: the investor owns none"))

    if v or rec.action not in TRADE_ACTIONS:
        return CheckResult(v, None if v else portfolio.model_copy(deep=True))

    value = rec.shares * price
    fees = value * fee_rate
    cash = portfolio.cash
    held = portfolio.shares_of(ticker)

    if rec.action is Action.SELL:
        if held == 0:
            v.append(Violation("sell_unowned", f"investor owns no {ticker}"))
        elif rec.shares > held:
            v.append(Violation("oversell", f"sell {rec.shares} {ticker} but only {held} held"))
        new_cash = cash + value - fees
        new_held = held - rec.shares
    else:  # BUY
        cost = value + fees
        if cost > cash + 1e-6:
            v.append(Violation("insufficient_cash", f"buy costs {cost:,.2f} but cash is {cash:,.2f}"))
        new_cash = cash - cost
        new_held = held + rec.shares

    if v:
        return CheckResult(v, None)

    others = [h for h in portfolio.holdings if h.ticker.upper() != ticker]
    holdings = others + ([Holding(ticker=ticker, shares=new_held)] if new_held else [])
    proposed = Portfolio(cash=round(new_cash, 2), currency=portfolio.currency, holdings=holdings)
    warnings = []
    if rec.action is Action.BUY:
        weight = weight_of(ticker, proposed, prices)
        if weight is not None and weight > CONCENTRATION_LIMIT:
            warnings.append(Violation("concentration", f"after the buy {ticker} is {weight:.1%} of the portfolio, "
                                                       f"above the {CONCENTRATION_LIMIT:.0%} limit"))
    return CheckResult([], proposed, warnings)


def weight_of(ticker: str, portfolio: Portfolio, prices: dict[str, float]) -> float | None:
    """Share of the portfolio's value (cash plus holdings at ``prices``) in ``ticker``."""
    px = {t.upper(): p for t, p in prices.items()}
    worth = {h.ticker.upper(): h.shares * px.get(h.ticker.upper(), 0.0) for h in portfolio.holdings}
    total = portfolio.cash + sum(worth.values())
    return worth.get(ticker.upper(), 0.0) / total if total else None
