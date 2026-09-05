from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from quantlab.backtest.trades import TradeLog
from quantlab.data.trust import DataTrustAssessment


@dataclass(frozen=True)
class BacktestResult:
    """
    Canonical output contract for a completed backtest.

    This object represents the complete outcome of the simulation.
    It deliberately keeps performance metrics, the realized equity
    curve, trade events, and Data Trust together so downstream
    consumers do not need to reach back into BacktestEngine state.

    A small mapping-style compatibility interface is retained so
    legacy consumers can continue using result["metric_name"].
    """

    metrics: dict[str, Any]
    equity_curve: pd.Series
    trade_log: TradeLog
    data_trust: DataTrustAssessment

    def __post_init__(self) -> None:
        if not isinstance(self.metrics, dict):
            raise TypeError("metrics must be a dictionary")

        if not isinstance(self.equity_curve, pd.Series):
            raise TypeError("equity_curve must be a pandas Series")

        if not isinstance(self.trade_log, TradeLog):
            raise TypeError("trade_log must be a TradeLog")

        if not isinstance(self.data_trust, DataTrustAssessment):
            raise TypeError(
                "data_trust must be a DataTrustAssessment"
            )

    def __getitem__(self, key: str) -> Any:
        """
        Backward-compatible access to performance metrics.

        Example:
            result["total_return"]

        The canonical interface remains:
            result.metrics["total_return"]
        """
        return self.metrics[key]
