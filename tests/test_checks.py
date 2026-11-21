import pytest

from egx_guide.checks import check_recommendation
from egx_guide.models import Action, Holding, Portfolio, Recommendation

PRICES = {"COMI": 80.0, "ETEL": 40.0}
BOOK = Portfolio(cash=10_000, holdings=[Holding(ticker="COMI", shares=100)])


def rec(action, ticker=None, shares=0):
    return Recommendation(action=action, ticker=ticker, shares=shares, explanation="x")


def rules(result):
    return {v.rule for v in result.violations}


def test_valid_buy_updates_cash_and_holdings():
    r = check_recommendation(rec(Action.BUY, "ETEL", 50), BOOK, PRICES)
    assert r.ok
    assert r.proposed.cash == 8_000
    assert r.proposed.shares_of("ETEL") == 50
    assert r.proposed.shares_of("COMI") == 100


def test_buy_with_fees_must_fit_cash():
    # 125 * 80 = 10,000 exactly; a 1% fee pushes it over.
    assert check_recommendation(rec(Action.BUY, "COMI", 125), BOOK, PRICES).ok
    r = check_recommendation(rec(Action.BUY, "COMI", 125), BOOK, PRICES, fee_rate=0.01)
    assert rules(r) == {"insufficient_cash"}


def test_sell_unowned_is_blocked():
    assert rules(check_recommendation(rec(Action.SELL, "ETEL", 10), BOOK, PRICES)) == {"sell_unowned"}


def test_oversell_is_blocked():
    assert rules(check_recommendation(rec(Action.SELL, "COMI", 101), BOOK, PRICES)) == {"oversell"}


def test_full_sell_removes_holding():
    r = check_recommendation(rec(Action.SELL, "comi", 100), BOOK, PRICES)
    assert r.ok
    assert r.proposed.holdings == []
    assert r.proposed.cash == 18_000


@pytest.mark.parametrize("action", [Action.BUY, Action.SELL])
def test_trade_needs_positive_shares(action):
    assert "positive_shares" in rules(check_recommendation(rec(action, "COMI", 0), BOOK, PRICES))


def test_trade_needs_known_price():
    assert "unknown_price" in rules(check_recommendation(rec(Action.BUY, "TMGH", 1), BOOK, PRICES))


@pytest.mark.parametrize("action", [Action.KEEP_CASH, Action.INSUFFICIENT_EVIDENCE])
def test_non_trades_leave_book_unchanged(action):
    r = check_recommendation(rec(action), BOOK, PRICES)
    assert r.ok and r.proposed == BOOK


def test_non_trade_with_shares_is_blocked():
    assert rules(check_recommendation(rec(Action.KEEP_CASH, shares=5), BOOK, PRICES)) == {"no_shares_without_trade"}


def test_hold_requires_ownership():
    assert check_recommendation(rec(Action.HOLD, "COMI"), BOOK, PRICES).ok
    assert rules(check_recommendation(rec(Action.HOLD, "ETEL"), BOOK, PRICES)) == {"hold_unowned"}
