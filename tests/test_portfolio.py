from __future__ import annotations

import numpy as np
import pandas as pd

from quantlab.portfolio.allocation import equal_weight_allocation, weight_portfolio
from quantlab.portfolio.risk import maximum_drawdown, sharpe_ratio, volatility
from quantlab.portfolio.returns import cumulative_returns, equity_curve, portfolio_returns


def make_price_frame() -> pd.DataFrame:
    dates = pd.date_range("2024-01-01", periods=5, freq="D")
    return pd.DataFrame(
        {
            "AAPL": [100.0, 102.0, 101.0, 105.0, 107.0],
            "MSFT": [90.0, 92.0, 91.0, 93.0, 95.0],
        },
        index=dates,
    )


def test_portfolio_returns_and_equity_curve():
    prices = make_price_frame()
    returns = portfolio_returns(prices)
    cum_returns = cumulative_returns(returns)
    equity = equity_curve(cum_returns)
    assert isinstance(returns, pd.Series)
    assert isinstance(cum_returns, pd.Series)
    assert isinstance(equity, pd.Series)
    assert np.isfinite(equity.iloc[-1])


def test_risk_metrics_are_numeric():
    returns = pd.Series([0.01, -0.02, 0.03, 0.04], dtype=float)
    assert np.isfinite(volatility(returns))
    assert np.isfinite(sharpe_ratio(returns))
    assert np.isfinite(maximum_drawdown(pd.Series([1.0, 1.1, 0.9, 1.2], dtype=float)))


def test_allocation_helpers():
    weights = equal_weight_allocation(["AAPL", "MSFT", "GOOG"])
    normalized = weight_portfolio(
        pd.Series(
            [1.0, 2.0, 3.0],
            index=["AAPL", "MSFT", "GOOG"],
        )
    )
    assert weights.sum() == 1.0
    assert normalized.sum() == 1.0
