from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass
class Trade:
    """Represents a single trade entry or exit event."""

    timestamp: pd.Timestamp
    symbol: str
    side: str
    price: float
    quantity: float


@dataclass
class TradeLog:
    """Container for a collection of trades."""

    trades: list[Trade] | None = None

    def __post_init__(self) -> None:
        if self.trades is None:
            self.trades = []

    def add_trade(self, trade: Trade) -> None:
        """Append a trade to the log."""
        self.trades.append(trade)
