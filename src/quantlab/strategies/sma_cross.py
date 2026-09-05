from __future__ import annotations

import pandas as pd

from quantlab.features.indicators import sma20, sma50
from quantlab.strategies.base import BaseStrategy


class SmaCrossStrategy(BaseStrategy):
    """Generate buy/sell signals from SMA20/SMA50 crossovers."""

    def __init__(self) -> None:
        super().__init__(name="sma_cross")

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        """Return a signal series based on moving-average crossovers."""
        signals = pd.Series(0, index=df.index, dtype=int)
        if df.empty:
            return signals

        sma20_series = sma20(df)
        sma50_series = sma50(df)
        signals[(sma20_series > sma50_series)] = 1
        signals[(sma20_series < sma50_series)] = -1
        return signals
