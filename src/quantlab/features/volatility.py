from __future__ import annotations

import numpy as np
import pandas as pd


def rolling_volatility(df: pd.DataFrame, window: int = 20) -> pd.Series:
    """Calculate rolling volatility from daily returns."""
    returns = df["Close"].pct_change().dropna()
    return returns.rolling(window=window).std() * np.sqrt(252)


def annualized_volatility(df: pd.DataFrame, window: int = 20) -> float:
    """Calculate annualized volatility from the latest rolling volatility value."""
    return float(rolling_volatility(df, window=window).dropna().iloc[-1])


def maximum_drawdown(df: pd.DataFrame) -> float:
    """Calculate the maximum drawdown from cumulative price growth."""
    cumulative = (1 + df["Close"].pct_change()).cumprod()
    running_max = cumulative.cummax()
    drawdown = (cumulative / running_max) - 1
    return float(drawdown.min())
