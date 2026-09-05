from __future__ import annotations

from quantlab.data.trust import DataTrustState
from quantlab.experiments.config import ExperimentConfig
from quantlab.experiments.result import ExperimentResult
from quantlab.experiments.runner import ExperimentRunner


def run_experiment(
    dataset_name: str,
    strategy_name: str,
    output_dir=None,
    position_size: float = 1.0,
    source_quality: DataTrustState = DataTrustState.TRUSTED,
) -> ExperimentResult:
    """Run a single experiment using the current QuantLab modules."""
    config = ExperimentConfig(
        dataset_name=dataset_name,
        strategy_name=strategy_name,
        source_quality=source_quality,
        output_dir=output_dir,
        position_size=position_size,
    )
    return ExperimentRunner().run(config)


__all__ = [
    "ExperimentConfig",
    "ExperimentResult",
    "ExperimentRunner",
    "run_experiment",
]
