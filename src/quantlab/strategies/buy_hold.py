from __future__ import annotations

import pandas as pd

from quantlab.strategies.base import BaseStrategy


class BuyHoldStrategy(BaseStrategy):
    """Simple buy-and-hold benchmark strategy."""

    def __init__(self) -> None:
        super().__init__(name="buy_hold")

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        """Buy once at the first valid row and hold thereafter."""
        signals = pd.Series(0, index=df.index, dtype=int)
        if df.empty:
            return signals
        signals.iloc[0] = 1
        return signals
