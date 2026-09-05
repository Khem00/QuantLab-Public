from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from quantlab.data.trust import DataTrustState


@dataclass
class ExperimentConfig:
    """Configuration for a single QuantLab experiment run."""

    dataset_name: str
    strategy_name: str
    source_quality: DataTrustState
    output_dir: str | Path | None = None
    initial_capital: float = 100000.0
    commission: float = 0.0
    slippage: float = 0.0
    position_size: float = 1.0

    def __post_init__(self) -> None:
        self.dataset_name = self.dataset_name.strip()
        self.strategy_name = self.strategy_name.strip()
        self.source_quality = DataTrustState(self.source_quality)

        if not self.dataset_name:
            raise ValueError("dataset_name must be a non-empty string")
        if not self.strategy_name:
            raise ValueError("strategy_name must be a non-empty string")
        if self.initial_capital <= 0:
            raise ValueError("initial_capital must be greater than zero")
        if self.commission < 0:
            raise ValueError("commission must be non-negative")
        if self.slippage < 0:
            raise ValueError("slippage must be non-negative")
        if self.position_size <= 0:
            raise ValueError("position_size must be greater than zero")

        if self.output_dir is not None:
            self.output_dir = Path(self.output_dir)
