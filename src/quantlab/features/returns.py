from __future__ import annotations

import numpy as np
import pandas as pd


def daily_returns(df: pd.DataFrame) -> pd.Series:
    """Calculate simple daily returns from a Close price series."""
    return df["Close"].pct_change()


def log_returns(df: pd.DataFrame) -> pd.Series:
    """Calculate log returns from a Close price series."""
    return np.log(df["Close"]).diff()


def cumulative_returns(df: pd.DataFrame) -> pd.Series:
    """Calculate cumulative simple returns from a Close price series."""
    return (1 + daily_returns(df)).cumprod() - 1
