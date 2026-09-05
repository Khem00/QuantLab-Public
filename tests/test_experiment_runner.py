from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd

from quantlab.backtest.result import BacktestResult
import pytest

from quantlab import run_experiment
from quantlab.data.trust import DataTrustAssessment, DataTrustState
from quantlab.experiments.config import ExperimentConfig
from quantlab.experiments.runner import ExperimentRunner


def test_runner_runs_valid_experiment(tmp_path: Path) -> None:
    config = ExperimentConfig(
        source_quality=DataTrustState.TRUSTED,
        dataset_name="AAPL_history",
        strategy_name="buy_hold",
        output_dir=tmp_path,
    )

    result = ExperimentRunner().run(config)

    assert result.status == "completed"
    assert result.metrics["total_return"] is not None
    assert result.summary_path.exists()
    assert result.summary_path.suffix == ".csv"


def test_runner_raises_for_unknown_strategy(tmp_path: Path) -> None:
    config = ExperimentConfig(
        source_quality=DataTrustState.TRUSTED,
        dataset_name="AAPL_history",
        strategy_name="unknown",
        output_dir=tmp_path,
    )

    try:
        ExperimentRunner().run(config)
    except ValueError as exc:
        assert "Unknown strategy" in str(exc)
    else:
        raise AssertionError("Expected ValueError for unknown strategy")


def test_runner_accepts_csv_dataset_name(tmp_path: Path) -> None:
    config = ExperimentConfig(
        source_quality=DataTrustState.TRUSTED,
        dataset_name="AAPL_history.csv",
        strategy_name="buy_hold",
        output_dir=tmp_path,
    )

    result = ExperimentRunner().run(config)

    assert result.status == "completed"
    assert result.summary_path.exists()


def test_runner_accepts_case_insensitive_strategy_name(tmp_path: Path) -> None:
    config = ExperimentConfig(
        source_quality=DataTrustState.TRUSTED,
        dataset_name="AAPL_history",
        strategy_name="BUY_HOLD",
        output_dir=tmp_path,
    )

    result = ExperimentRunner().run(config)

    assert result.status == "completed"


def test_package_entrypoint_runs_experiment(tmp_path: Path) -> None:
    result = run_experiment(
        "AAPL_history",
        "buy_hold",
        output_dir=tmp_path,
    )

    assert result.status == "completed"
    assert result.summary_path.exists()


def test_package_entrypoint_passes_position_size_to_config(tmp_path: Path) -> None:
    captured_config = {}

    def fake_run(self, config):
        captured_config["position_size"] = config.position_size
        return type(
            "DummyResult",
            (),
            {
                "status": "completed",
                "metrics": {},
                "summary_path": tmp_path / "summary.csv",
            },
        )()

    with patch(
        "quantlab.experiments.runner.ExperimentRunner.run",
        new=fake_run,
    ):
        run_experiment(
            "AAPL_history",
            "buy_hold",
            output_dir=tmp_path,
            position_size=0.25,
        )

    assert captured_config["position_size"] == 0.25


def test_runner_builds_summary_from_backtest_metrics(tmp_path: Path) -> None:
    runner = ExperimentRunner()

    config = ExperimentConfig(
        source_quality=DataTrustState.TRUSTED,
        dataset_name="AAPL_history",
        strategy_name="buy_hold",
        output_dir=tmp_path,
    )

    captured_payload = {}

    def fake_summary(payload, *args, **kwargs):
        captured_payload["payload"] = payload
        return pd.DataFrame(
            {"total_return": [0.1]},
            index=["portfolio"],
        )

    dataset = pd.DataFrame(
        {
            "Date": pd.date_range(
                "2024-01-01",
                periods=2,
                freq="D",
            ),
            "Symbol": ["AAPL", "AAPL"],
            "Close": [100.0, 110.0],
        }
    )

    trust = DataTrustAssessment(
        state=DataTrustState.TRUSTED,
        capability="backtest",
        suitable=True,
    )

    with patch(
        "quantlab.experiments.runner.load_validated_dataset"
    ) as mock_load, \
        patch(
            "quantlab.experiments.runner.validate_strategy_input",
            side_effect=lambda df: df,
        ), \
        patch(
            "quantlab.experiments.runner.build_summary",
            side_effect=fake_summary,
        ) as mock_summary, \
        patch(
            "quantlab.experiments.runner.export_summary"
        ) as mock_export, \
        patch(
            "quantlab.experiments.runner.save_processed_data"
        ):

        mock_load.return_value = (dataset, trust)

        mock_export.return_value = (
            tmp_path / "experiment_summary.csv"
        )

        result = runner.run(config)

    assert result.metrics["total_return"] is not None
    assert mock_summary.call_count == 1

    assert isinstance(
        captured_payload["payload"],
        BacktestResult,
    )

    assert captured_payload["payload"] is result.backtest

    assert (
        captured_payload["payload"].equity_curve
        is result.backtest.equity_curve
    )

    assert (
        captured_payload["payload"].metrics
        is result.backtest.metrics
    )


def test_config_rejects_empty_required_fields() -> None:
    try:
        ExperimentConfig(
            source_quality=DataTrustState.TRUSTED,
            dataset_name="",
            strategy_name="buy_hold",
        )
    except ValueError as exc:
        assert "dataset_name" in str(exc)
    else:
        raise AssertionError(
            "Expected ValueError for empty dataset_name"
        )


def test_config_rejects_non_positive_capital() -> None:
    try:
        ExperimentConfig(
            source_quality=DataTrustState.TRUSTED,
            dataset_name="AAPL_history",
            strategy_name="buy_hold",
            initial_capital=0.0,
        )
    except ValueError as exc:
        assert "initial_capital" in str(exc)
    else:
        raise AssertionError(
            "Expected ValueError for non-positive capital"
        )


def test_runner_rejects_invalid_strategy_signals(tmp_path: Path) -> None:
    config = ExperimentConfig(
        source_quality=DataTrustState.TRUSTED,
        dataset_name="AAPL_history",
        strategy_name="buy_hold",
        output_dir=tmp_path,
    )

    class InvalidStrategy:
        def generate_signals(self, df: pd.DataFrame) -> pd.Series:
            return pd.Series(
                [0, 2],
                index=df.index,
                dtype=int,
            )

    runner = ExperimentRunner()

    with patch.object(
        runner,
        "_resolve_strategy",
        return_value=InvalidStrategy(),
    ), \
        patch(
            "quantlab.experiments.runner.load_validated_dataset"
        ) as mock_load:

        dataset = pd.DataFrame(
            {
                "Date": pd.date_range(
                    "2024-01-01",
                    periods=2,
                    freq="D",
                ),
                "Symbol": ["AAPL", "AAPL"],
                "Open": [100.0, 105.0],
                "High": [101.0, 111.0],
                "Low": [99.0, 104.0],
                "Close": [100.0, 110.0],
                "Volume": [1000.0, 1000.0],
            }
        )

        trust = DataTrustAssessment(
            state=DataTrustState.TRUSTED,
            capability="backtest",
            suitable=True,
        )

        mock_load.return_value = (dataset, trust)

        try:
            runner.run(config)
        except ValueError as exc:
            assert "-1, 0, or 1" in str(exc)
        else:
            raise AssertionError(
                "Expected invalid strategy signals to be rejected"
            )


def test_runner_enforces_data_strategy_contract(tmp_path: Path) -> None:
    config = ExperimentConfig(
        source_quality=DataTrustState.TRUSTED,
        dataset_name="AAPL_history",
        strategy_name="buy_hold",
        output_dir=tmp_path,
    )

    runner = ExperimentRunner()

    invalid_dataset = pd.DataFrame(
        {
            "Date": pd.to_datetime(
                ["2024-01-02", "2024-01-01"]
            ),
            "Symbol": ["AAPL", "AAPL"],
            "Open": [101.0, 100.0],
            "High": [102.0, 101.0],
            "Low": [100.0, 99.0],
            "Close": [101.0, 100.0],
            "Volume": [1000.0, 1000.0],
        }
    )

    trust = DataTrustAssessment(
        state=DataTrustState.TRUSTED,
        capability="backtest",
        suitable=True,
    )

    with patch(
        "quantlab.experiments.runner.load_validated_dataset",
        return_value=(invalid_dataset, trust),
    ):

        with pytest.raises(
            ValueError,
            match="sorted ascending",
        ):
            runner.run(config)


def test_runner_enforces_strategy_input_contract(tmp_path: Path) -> None:
    config = ExperimentConfig(
        source_quality=DataTrustState.TRUSTED,
        dataset_name="AAPL_history",
        strategy_name="buy_hold",
        output_dir=tmp_path,
    )

    runner = ExperimentRunner()

    with patch.object(
        runner,
        "_resolve_strategy",
    ) as mock_strategy, \
        patch(
            "quantlab.experiments.runner.load_validated_dataset"
        ) as mock_load:

        dataset = pd.DataFrame(
            {
                "Date": pd.date_range(
                    "2024-01-01",
                    periods=2,
                    freq="D",
                ),
                "Symbol": ["AAPL", "AAPL"],
                "Open": [100.0, 105.0],
                "High": [101.0, 111.0],
                "Low": [99.0, 104.0],
                "Close": [100.0, -10.0],
                "Volume": [1000.0, 1000.0],
            }
        )

        trust = DataTrustAssessment(
            state=DataTrustState.TRUSTED,
            capability="backtest",
            suitable=True,
        )

        mock_load.return_value = (dataset, trust)

        generate_signals = MagicMock(
            return_value=pd.Series(
                [1, 0],
                index=dataset.index,
                dtype=int,
            )
        )

        mock_strategy.return_value = MagicMock(
            generate_signals=generate_signals,
        )

        with pytest.raises(
            ValueError,
            match="positive values",
        ):
            runner.run(config)

        generate_signals.assert_not_called()
