from __future__ import annotations

import pandas as pd

from quantlab.features.indicators import rsi14
from quantlab.strategies.base import BaseStrategy


class RsiStrategy(BaseStrategy):
    """Generate buy/sell signals from RSI thresholds."""

    def __init__(self, overbought: int = 70, oversold: int = 30) -> None:
        super().__init__(name="rsi")
        self.overbought = overbought
        self.oversold = oversold

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        """Return a signal series based on RSI thresholds."""
        signals = pd.Series(0, index=df.index, dtype=int)
        if df.empty:
            return signals

        rsi = rsi14(df)
        signals[rsi > self.overbought] = -1
        signals[rsi < self.oversold] = 1
        return signals
