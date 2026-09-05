from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict

import pandas as pd


@dataclass
class Portfolio:
    """Simple portfolio state for a backtest."""

    initial_capital: float
    cash: float = field(init=False)
    positions: Dict[str, float] = field(default_factory=dict, init=False)
    portfolio_value: float = field(init=False)

    def __post_init__(self) -> None:
        self.cash = float(self.initial_capital)
        self.portfolio_value = float(self.initial_capital)

    def update_value(self, prices: pd.Series) -> float:
        """Recalculate portfolio value using current close prices."""
        position_value = sum(
            self.positions.get(symbol, 0.0) * prices.get(symbol, 0.0)
            for symbol in self.positions
        )
        self.portfolio_value = self.cash + position_value
        return self.portfolio_value

    def update_value_for_symbol(
        self,
        symbol: str,
        price: float,
    ) -> float:
        """Recalculate portfolio value using one current symbol price."""
        position_value = self.positions.get(symbol, 0.0) * price
        self.portfolio_value = self.cash + position_value
        return self.portfolio_value
