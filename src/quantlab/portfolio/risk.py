from __future__ import annotations

import numpy as np
import pandas as pd


def volatility(returns: pd.Series, periods_per_year: int = 252) -> float:
    """Calculate annualized volatility from a return series."""
    if returns.empty:
        return 0.0
    return float(returns.std() * np.sqrt(periods_per_year))


def sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.0, periods_per_year: int = 252) -> float:
    """Calculate the Sharpe ratio for a return series."""
    if returns.empty:
        return 0.0
    std = returns.std()
    if std == 0:
        return 0.0
    return float((returns.mean() - risk_free_rate) / std * np.sqrt(periods_per_year))


def maximum_drawdown(equity_curve: pd.Series) -> float:
    """Calculate the maximum drawdown from an equity curve."""
    if equity_curve.empty:
        return 0.0
    running_max = equity_curve.cummax()
    drawdown = (equity_curve / running_max) - 1
    return float(drawdown.min())
