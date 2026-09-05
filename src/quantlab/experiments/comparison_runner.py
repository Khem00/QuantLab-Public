from __future__ import annotations

import pandas as pd

from quantlab.backtest.engine import BacktestEngine
from quantlab.data.loading import load_all_datasets
from quantlab.data.normalize import normalize_all_datasets
from quantlab.data.trust import assess_data_trust
from quantlab.data.validate import validate_datasets
from quantlab.experiments.config import ExperimentConfig
from quantlab.experiments.result import (
    ExperimentArtifacts,
    ExperimentResult,
)
from quantlab.portfolio.trade_statistics import calculate_trade_statistics
from quantlab.signals.validation import validate_signal_series
from quantlab.strategies.input_contract import validate_strategy_input
from quantlab.strategies.registry import get_strategy, list_strategies


class StrategyComparisonRunner:
    """
    Run multiple registered strategies against the same dataset.

    Every strategy passes through the same data, signal, and backtest
    contracts used by the single-experiment runner.
    """

    def __init__(self) -> None:
        pass

    def _normalize_dataset_name(self, dataset_name: str) -> str:
        normalized = dataset_name.strip()

        if normalized.endswith(".csv"):
            normalized = normalized[:-4]

        return normalized

    def run(
        self,
        config: ExperimentConfig,
    ) -> dict[str, ExperimentResult]:
        """
        Execute all registered strategies and return canonical results.

        Each strategy produces a BacktestResult, which is then wrapped
        in an ExperimentResult together with experiment-level metadata
        and artifacts.
        """

        raw_datasets = load_all_datasets()

        normalized_datasets = normalize_all_datasets(
            raw_datasets
        )

        validation_results = validate_datasets(
            normalized_datasets
        )

        dataset_key = self._normalize_dataset_name(
            config.dataset_name
        )

        validation_result = validation_results.get(
            dataset_key,
            {},
        )

        if not validation_result.get(
            "is_valid",
            False,
        ):
            raise ValueError(
                f"Dataset {config.dataset_name} failed validation"
            )

        dataset = normalized_datasets[dataset_key]

        # Canonical validation -> capability-specific Data Trust.
        backtest_trust = assess_data_trust(
            capability="backtest",
            validation_passed=bool(
                validation_result.get("is_valid", False)
            ),
            reasons=tuple(
                str(issue)
                for issue in validation_result.get("issues", [])
            ),
        )

        # Data -> Strategy trust boundary.
        dataset = validate_strategy_input(dataset)

        results: dict[str, ExperimentResult] = {}

        for strategy_name in list_strategies():

            strategy = get_strategy(strategy_name)

            # Strategy generates raw signals.
            signals = strategy.generate_signals(dataset)

            # Strategy -> Signal trust boundary.
            signals = validate_signal_series(
                signals,
                expected_index=dataset.index,
            )

            signal_frame = pd.DataFrame(
                {
                    "Date": dataset["Date"],
                    "Symbol": dataset["Symbol"],
                    "Signal": signals,
                }
            )

            engine = BacktestEngine(
                initial_capital=config.initial_capital,
                commission=config.commission,
                slippage=config.slippage,
                position_size=config.position_size,
            )

            # BacktestEngine owns simulation state and returns the
            # canonical BacktestResult.
            backtest = engine.run(
                dataset,
                signal_frame,
                trust_assessment=backtest_trust,
            )

            trade_statistics = calculate_trade_statistics(
                backtest.trade_log
            )

            artifacts = ExperimentArtifacts()

            results[strategy_name] = ExperimentResult(
                status="completed",
                dataset_name=dataset_key,
                strategy_name=strategy_name,
                configuration=config,
                backtest=backtest,
                trade_statistics=trade_statistics,
                artifacts=artifacts,
            )

        return results
