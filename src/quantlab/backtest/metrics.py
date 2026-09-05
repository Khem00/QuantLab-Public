from __future__ import annotations

import numpy as np
import pandas as pd


def total_return(values: pd.Series) -> float:
    """Calculate total return from a series of portfolio values."""
    return float(values.iloc[-1] / values.iloc[0] - 1)


def annualized_return(values: pd.Series, periods_per_year: int = 252) -> float:
    """Calculate annualized return from a series of portfolio values."""
    total_ret = values.iloc[-1] / values.iloc[0] - 1
    return float((1 + total_ret) ** (periods_per_year / len(values)) - 1)


def sharpe_ratio(values: pd.Series, risk_free_rate: float = 0.0, periods_per_year: int = 252) -> float:
    """Calculate the Sharpe ratio from portfolio return series."""
    returns = values.pct_change().dropna()
    if returns.std() == 0:
        return 0.0
    return float((returns.mean() - risk_free_rate) / returns.std() * np.sqrt(periods_per_year))


def maximum_drawdown(values: pd.Series) -> float:
    """Calculate the maximum drawdown from a series of portfolio values."""
    running_max = values.cummax()
    drawdown = (values / running_max) - 1
    return float(drawdown.min())


def volatility(values: pd.Series, periods_per_year: int = 252) -> float:
    """Calculate annualized volatility from portfolio return series."""
    returns = values.pct_change().dropna()
    if returns.empty:
        return 0.0
    return float(returns.std() * np.sqrt(periods_per_year))
