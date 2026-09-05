from __future__ import annotations

from pathlib import Path

import pandas as pd

from quantlab.backtest.engine import BacktestEngine
from quantlab.config import RAW_DATA_DIR
from quantlab.data.boundary import load_validated_dataset
from quantlab.data.normalize import save_processed_data
from quantlab.data.trust import (
    DataTrustState,
    require_data_trust,
)
from quantlab.experiments.config import ExperimentConfig
from quantlab.experiments.result import (
    ExperimentArtifacts,
    ExperimentResult,
)
from quantlab.portfolio.trade_statistics import calculate_trade_statistics
from quantlab.reports.export import export_summary
from quantlab.reports.summary import build_summary
from quantlab.signals.validation import validate_signal_series
from quantlab.strategies.input_contract import validate_strategy_input
from quantlab.strategies.registry import get_strategy


class ExperimentRunner:
    """Orchestrate one complete QuantLab experiment."""

    def __init__(self) -> None:
        pass

    def _normalize_dataset_name(self, dataset_name: str) -> str:
        normalized = dataset_name.strip()

        if normalized.endswith(".csv"):
            normalized = normalized[:-4]

        return normalized

    def _resolve_strategy(self, strategy_name: str):
        return get_strategy(strategy_name)

    def run(self, config: ExperimentConfig) -> ExperimentResult:
        dataset_key = self._normalize_dataset_name(
            config.dataset_name
        )

        dataset_path = RAW_DATA_DIR / f"{dataset_key}.csv"

        dataset, backtest_trust = load_validated_dataset(
            dataset_path,
            capability="backtest",
            source_quality=config.source_quality,
        )

        require_data_trust(
            backtest_trust,
            allowed_states={
                DataTrustState.TRUSTED,
                DataTrustState.CONDITIONALLY_TRUSTED,
            },
        )

        dataset = validate_strategy_input(dataset)

        strategy = self._resolve_strategy(
            config.strategy_name
        )

        signals = strategy.generate_signals(dataset)

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

        backtest = engine.run(
            dataset,
            signal_frame,
            trust_assessment=backtest_trust,
        )

        output_dir = Path(
            config.output_dir or "reports"
        )

        output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        equity_curve_path = (
            output_dir / "equity_curve.csv"
        )

        backtest.equity_curve.to_csv(
            equity_curve_path,
            header=["Portfolio_Value"],
        )

        summary = build_summary(
            backtest,
        )

        summary_path = export_summary(
            summary,
            output_dir / "experiment_summary.csv",
        )

        processed_data_dir = (
            output_dir / "processed"
        )

        save_processed_data(
            {dataset_key: dataset},
            processed_data_dir,
        )

        trade_statistics = calculate_trade_statistics(
            backtest.trade_log
        )

        artifacts = ExperimentArtifacts(
            summary_path=summary_path,
            equity_curve_path=equity_curve_path,
            processed_data_path=processed_data_dir,
        )

        return ExperimentResult(
            status="completed",
            dataset_name=dataset_key,
            strategy_name=config.strategy_name,
            configuration=config,
            backtest=backtest,
            trade_statistics=trade_statistics,
            artifacts=artifacts,
        )
