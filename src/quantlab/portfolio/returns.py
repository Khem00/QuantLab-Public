from __future__ import annotations

import pandas as pd


def portfolio_returns(prices: pd.DataFrame) -> pd.Series:
    """Calculate simple portfolio returns from a wide DataFrame of asset prices."""
    if prices.empty:
        return pd.Series(dtype=float)
    return prices.pct_change().mean(axis=1)


def cumulative_returns(returns: pd.Series) -> pd.Series:
    """Convert simple returns into cumulative returns."""
    if returns.empty:
        return pd.Series(dtype=float)
    return (1 + returns).cumprod() - 1


def equity_curve(cumulative_returns: pd.Series) -> pd.Series:
    """Create an equity curve starting from 1.0."""
    if cumulative_returns.empty:
        return pd.Series(dtype=float)
    return 1 + cumulative_returns
