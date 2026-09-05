from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from quantlab.backtest.result import BacktestResult
from quantlab.data.trust import (
    DataTrustAssessment,
    DataTrustState,
)
from quantlab.experiments.comparison_runner import StrategyComparisonRunner
from quantlab.experiments.config import ExperimentConfig


def make_dataset() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Date": pd.date_range(
                "2024-01-01",
                periods=4,
                freq="D",
            ),
            "Symbol": ["AAPL"] * 4,
            "Close": [100.0, 102.0, 104.0, 106.0],
        }
    )


def make_config(tmp_path: Path) -> ExperimentConfig:
    return ExperimentConfig(
        dataset_name="AAPL_history",
        strategy_name="comparison",
        source_quality=DataTrustState.TRUSTED,
        output_dir=tmp_path,
    )


def make_backtest_result(
    dataset: pd.DataFrame,
    *,
    metrics: dict | None = None,
) -> BacktestResult:
    from quantlab.backtest.trades import TradeLog

    return BacktestResult(
        metrics=metrics or {
            "total_return": 0.1,
            "sharpe_ratio": 1.0,
        },
        equity_curve=pd.Series(
            [100000.0, 101000.0, 102000.0, 103000.0],
            index=dataset.index,
            dtype=float,
        ),
        trade_log=TradeLog(),
        data_trust=DataTrustAssessment(
            state=DataTrustState.TRUSTED,
            capability="backtest",
            suitable=True,
        ),
    )


def patch_dataset(dataset: pd.DataFrame):
    return (
        patch(
            "quantlab.experiments.comparison_runner.load_all_datasets",
            return_value={"AAPL_history": dataset},
        ),
        patch(
            "quantlab.experiments.comparison_runner.normalize_all_datasets",
            return_value={"AAPL_history": dataset},
        ),
        patch(
            "quantlab.experiments.comparison_runner.validate_datasets",
            return_value={"AAPL_history": {"is_valid": True}},
        ),
    )


def test_comparison_runner_runs_all_registered_strategies(
    tmp_path: Path,
):
    dataset = make_dataset()
    config = make_config(tmp_path)

    fake_strategies = [
        "strategy_a",
        "strategy_b",
    ]

    def make_strategy():
        strategy = MagicMock()
        strategy.generate_signals.return_value = pd.Series(
            [1, 0, 1, 0],
            index=dataset.index,
            dtype=int,
        )
        return strategy

    load_patch, normalize_patch, validate_patch = patch_dataset(
        dataset
    )

    with load_patch, normalize_patch, validate_patch, \
         patch(
             "quantlab.experiments.comparison_runner.list_strategies",
             return_value=fake_strategies,
         ), \
         patch(
             "quantlab.experiments.comparison_runner.get_strategy",
             side_effect=lambda _: make_strategy(),
         ):

        results = StrategyComparisonRunner().run(config)

    assert set(results) == set(fake_strategies)

    for strategy_name, result in results.items():
        assert result.status == "completed"
        assert result.dataset_name == "AAPL_history"
        assert result.strategy_name == strategy_name
        assert result.configuration == config
        assert isinstance(result.backtest, BacktestResult)
        assert result.metrics
        assert result.trade_statistics is not None
        assert result.artifacts is not None


def test_comparison_runner_accepts_csv_dataset_name(
    tmp_path: Path,
):
    dataset = make_dataset()

    config = ExperimentConfig(
        dataset_name="AAPL_history.csv",
        strategy_name="comparison",
        source_quality=DataTrustState.TRUSTED,
        output_dir=tmp_path,
    )

    load_patch, normalize_patch, validate_patch = patch_dataset(
        dataset
    )

    with load_patch, normalize_patch, validate_patch, \
         patch(
             "quantlab.experiments.comparison_runner.list_strategies",
             return_value=[],
         ):

        results = StrategyComparisonRunner().run(config)

    assert results == {}


def test_comparison_runner_rejects_invalid_dataset(
    tmp_path: Path,
):
    dataset = make_dataset()
    config = make_config(tmp_path)

    load_patch, normalize_patch, validate_patch = patch_dataset(
        dataset
    )

    validate_patch = patch(
        "quantlab.experiments.comparison_runner.validate_datasets",
        return_value={
            "AAPL_history": {
                "is_valid": False,
            }
        },
    )

    with load_patch, normalize_patch, validate_patch:
        with pytest.raises(
            ValueError,
            match="failed validation",
        ):
            StrategyComparisonRunner().run(config)


def test_comparison_runner_enforces_strategy_input_contract(
    tmp_path: Path,
):
    dataset = make_dataset()
    dataset.loc[0, "Close"] = -10.0

    config = make_config(tmp_path)

    load_patch, normalize_patch, validate_patch = patch_dataset(
        dataset
    )

    with load_patch, normalize_patch, validate_patch, \
         patch(
             "quantlab.experiments.comparison_runner.list_strategies",
             return_value=["strategy_a"],
         ), \
         patch(
             "quantlab.experiments.comparison_runner.get_strategy",
         ) as mock_get_strategy:

        with pytest.raises(
            ValueError,
            match="positive values",
        ):
            StrategyComparisonRunner().run(config)

        mock_get_strategy.assert_not_called()


def test_comparison_runner_enforces_signal_contract(
    tmp_path: Path,
):
    dataset = make_dataset()
    config = make_config(tmp_path)

    invalid_signals = pd.Series(
        [1, 2, 0, 1],
        index=dataset.index,
        dtype=int,
    )

    strategy = MagicMock()
    strategy.generate_signals.return_value = invalid_signals

    load_patch, normalize_patch, validate_patch = patch_dataset(
        dataset
    )

    with load_patch, normalize_patch, validate_patch, \
         patch(
             "quantlab.experiments.comparison_runner.list_strategies",
             return_value=["strategy_a"],
         ), \
         patch(
             "quantlab.experiments.comparison_runner.get_strategy",
             return_value=strategy,
         ):

        with pytest.raises(
            ValueError,
            match="-1, 0, or 1",
        ):
            StrategyComparisonRunner().run(config)


def test_comparison_runner_preserves_position_size(
    tmp_path: Path,
):
    dataset = make_dataset()

    config = ExperimentConfig(
        dataset_name="AAPL_history",
        strategy_name="comparison",
        source_quality=DataTrustState.TRUSTED,
        output_dir=tmp_path,
        position_size=0.25,
    )

    strategy = MagicMock()
    strategy.generate_signals.return_value = pd.Series(
        [1, 0, 1, 0],
        index=dataset.index,
        dtype=int,
    )

    load_patch, normalize_patch, validate_patch = patch_dataset(
        dataset
    )

    captured_engine_kwargs = {}

    class FakeEngine:
        def __init__(self, **kwargs):
            captured_engine_kwargs.update(kwargs)

        def run(
            self,
            dataset,
            signal_frame,
            *,
            trust_assessment,
        ):
            return make_backtest_result(dataset)

    with load_patch, normalize_patch, validate_patch, \
         patch(
             "quantlab.experiments.comparison_runner.list_strategies",
             return_value=["strategy_a"],
         ), \
         patch(
             "quantlab.experiments.comparison_runner.get_strategy",
             return_value=strategy,
         ), \
         patch(
             "quantlab.experiments.comparison_runner.BacktestEngine",
             FakeEngine,
         ), \
         patch(
             "quantlab.experiments.comparison_runner.calculate_trade_statistics",
             return_value={"total_trades": 1},
         ):

        results = StrategyComparisonRunner().run(config)

    assert captured_engine_kwargs["position_size"] == 0.25
    assert results["strategy_a"].trade_statistics == {
        "total_trades": 1,
    }
    assert isinstance(
        results["strategy_a"].backtest,
        BacktestResult,
    )
