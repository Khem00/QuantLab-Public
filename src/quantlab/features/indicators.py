from __future__ import annotations

import numpy as np
import pandas as pd


def sma20(df: pd.DataFrame) -> pd.Series:
    """Calculate a 20-period simple moving average from Close prices."""
    return df["Close"].rolling(window=20).mean()


def sma50(df: pd.DataFrame) -> pd.Series:
    """Calculate a 50-period simple moving average from Close prices."""
    return df["Close"].rolling(window=50).mean()


def ema20(df: pd.DataFrame) -> pd.Series:
    """Calculate a 20-period exponential moving average from Close prices."""
    return df["Close"].ewm(span=20, adjust=False).mean()


def ema50(df: pd.DataFrame) -> pd.Series:
    """Calculate a 50-period exponential moving average from Close prices."""
    return df["Close"].ewm(span=50, adjust=False).mean()


def rsi14(df: pd.DataFrame, window: int = 14) -> pd.Series:
    """Calculate the Relative Strength Index (RSI) over a given window."""
    close = df["Close"].astype(float)
    delta = close.diff()
    gain = delta.clip(lower=0).rolling(window=window).mean()
    loss = (-delta.clip(upper=0)).rolling(window=window).mean()
    rs = gain / loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))
