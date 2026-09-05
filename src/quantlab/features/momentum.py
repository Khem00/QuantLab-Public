from __future__ import annotations

import pandas as pd


def momentum_10d(df: pd.DataFrame) -> pd.Series:
    """Calculate 10-day momentum as the percentage change over 10 periods."""
    return df["Close"].pct_change(periods=10)


def momentum_30d(df: pd.DataFrame) -> pd.Series:
    """Calculate 30-day momentum as the percentage change over 30 periods."""
    return df["Close"].pct_change(periods=30)
