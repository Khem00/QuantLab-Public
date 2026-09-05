from __future__ import annotations

import pandas as pd

import numpy as np
import pytest

from quantlab.backtest.result import BacktestResult
from quantlab.backtest.trades import TradeLog
from quantlab.data.trust import DataTrustAssessment, DataTrustState
from quantlab.reports.charts import plot_cumulative_returns, plot_drawdown, plot_equity_curve, plot_strategy_comparison
from quantlab.reports.export import export_summary
from quantlab.reports.summary import build_summary, compare_summaries


def make_price_frame() -> pd.DataFrame:
    dates = pd.date_range("2024-01-01", periods=5, freq="D")
    return pd.DataFrame(
        {
            "AAPL": [100.0, 102.0, 101.0, 105.0, 107.0],
            "MSFT": [90.0, 92.0, 91.0, 93.0, 95.0],
        },
        index=dates,
    )


def test_build_summary_and_compare_summaries():
    prices = make_price_frame()
    summary = build_summary(prices)
    comparison = compare_summaries({"strategy_a": summary, "strategy_b": summary})
    assert isinstance(summary, pd.DataFrame)
    assert comparison.shape[0] == 2


def test_charts_return_axis_objects():
    prices = make_price_frame()
    summary = build_summary(prices)
    equity = summary.iloc[0][["total_return"]]
    assert plot_equity_curve(pd.Series([1.0, 1.1, 1.2])).__class__.__name__ != "NoneType"
    assert plot_cumulative_returns(pd.Series([0.0, 0.1, 0.2])).__class__.__name__ != "NoneType"
    assert plot_drawdown(pd.Series([1.0, 0.95, 1.0])).__class__.__name__ != "NoneType"
    assert plot_strategy_comparison({"a": pd.Series([1.0, 1.1]), "b": pd.Series([1.0, 1.05])}).__class__.__name__ != "NoneType"


def test_export_summary_writes_csv(tmp_path):
    summary = pd.DataFrame({"metric": ["total_return"], "value": [0.1]})
    output_path = tmp_path / "summary.csv"
    exported = export_summary(summary, output_path)
    assert exported.exists()
    assert exported.suffix == ".csv"


def test_build_summary_uses_equity_curve_metrics():
    equity_curve = pd.Series([100.0, 110.0, 99.0], index=pd.date_range("2024-01-01", periods=3, freq="D"))

    summary = build_summary(equity_curve)

    assert summary.loc["portfolio", "total_return"] == pytest.approx(-0.01)
    assert summary.loc["portfolio", "max_drawdown"] < 0
    assert np.isfinite(summary.loc["portfolio", "volatility"])
    assert np.isfinite(summary.loc["portfolio", "sharpe_ratio"])


def test_build_summary_uses_canonical_backtest_metrics():
    equity_curve = pd.Series(
        [100.0, 110.0, 99.0],
        index=pd.date_range(
            "2024-01-01",
            periods=3,
            freq="D",
        ),
    )

    canonical_metrics = {
        "total_return": 0.42,
        "volatility": 0.31,
        "sharpe_ratio": 2.25,
        "max_drawdown": -0.11,
    }

    result = BacktestResult(
        metrics=canonical_metrics,
        equity_curve=equity_curve,
        trade_log=TradeLog(),
        data_trust=DataTrustAssessment(
            state=DataTrustState.TRUSTED,
            capability="backtest",
            suitable=True,
        ),
    )

    summary = build_summary(result)

    assert summary.loc["portfolio", "total_return"] == pytest.approx(0.42)
    assert summary.loc["portfolio", "volatility"] == pytest.approx(0.31)
    assert summary.loc["portfolio", "sharpe_ratio"] == pytest.approx(2.25)
    assert summary.loc["portfolio", "max_drawdown"] == pytest.approx(-0.11)


def test_build_summary_accepts_canonical_backtest_result():
    equity_curve = pd.Series(
        [100.0, 110.0, 99.0],
        index=pd.date_range(
            "2024-01-01",
            periods=3,
            freq="D",
        ),
    )

    metrics = {
        "total_return": 0.1,
        "volatility": 0.2,
        "sharpe_ratio": 1.0,
        "max_drawdown": -0.05,
    }

    result = BacktestResult(
        metrics=metrics,
        equity_curve=equity_curve,
        trade_log=TradeLog(),
        data_trust=DataTrustAssessment(
            state=DataTrustState.TRUSTED,
            capability="backtest",
            suitable=True,
        ),
    )

    summary = build_summary(result)

    assert summary.loc["portfolio", "total_return"] == pytest.approx(0.1)
    assert summary.loc["portfolio", "volatility"] == pytest.approx(0.2)
    assert summary.loc["portfolio", "sharpe_ratio"] == pytest.approx(1.0)
    assert summary.loc["portfolio", "max_drawdown"] == pytest.approx(-0.05)
from pathlib import Path

from quantlab.experiments.config import ExperimentConfig
from quantlab.experiments.result import (
    ExperimentArtifacts,
    ExperimentResult,
)
from quantlab.reports.comparison import build_strategy_comparison


def make_comparison_experiment_result(
    *,
    strategy_name: str = "strategy_a",
    metrics: dict | None = None,
    trust_state: DataTrustState = DataTrustState.TRUSTED,
    suitable: bool = True,
    capability: str = "backtest",
) -> ExperimentResult:
    equity_curve = pd.Series(
        [100.0, 101.0, 102.0],
        index=pd.date_range(
            "2024-01-01",
            periods=3,
            freq="D",
        ),
    )

    backtest = BacktestResult(
        metrics=metrics
        or {
            "total_return": 0.10,
            "annualized_return": 0.12,
            "sharpe_ratio": 1.50,
            "max_drawdown": -0.05,
            "volatility": 0.20,
        },
        equity_curve=equity_curve,
        trade_log=TradeLog(),
        data_trust=DataTrustAssessment(
            state=trust_state,
            capability=capability,
            suitable=suitable,
            reasons=("test reason",),
            evidence=("test evidence",),
        ),
    )

    return ExperimentResult(
        status="completed",
        dataset_name="AAPL_history",
        strategy_name=strategy_name,
        configuration=ExperimentConfig(
            dataset_name="AAPL_history",
            strategy_name=strategy_name,
            source_quality=DataTrustState.TRUSTED,
            output_dir=Path("."),
        ),
        backtest=backtest,
        trade_statistics={"total_trades": 1},
        artifacts=ExperimentArtifacts(),
    )


def test_strategy_comparison_projects_canonical_metrics_and_trust():
    result = make_comparison_experiment_result()

    comparison = build_strategy_comparison(
        {"strategy_a": result},
    )

    row = comparison.iloc[0]

    assert row["strategy"] == "strategy_a"
    assert row["total_return"] == pytest.approx(0.10)
    assert row["annualized_return"] == pytest.approx(0.12)
    assert row["sharpe_ratio"] == pytest.approx(1.50)
    assert row["max_drawdown"] == pytest.approx(-0.05)
    assert row["volatility"] == pytest.approx(0.20)

    assert row["data_trust_state"] == "trusted"
    assert row["data_trust_suitable"] is True
    assert row["data_trust_capability"] == "backtest"


def test_strategy_comparison_derives_projection_from_canonical_result():
    metrics = {
        "total_return": 0.42,
        "annualized_return": 0.55,
        "sharpe_ratio": 2.25,
        "max_drawdown": -0.11,
        "volatility": 0.31,
    }

    result = make_comparison_experiment_result(
        metrics=metrics,
    )

    comparison = build_strategy_comparison(
        {"strategy_a": result},
    )

    assert comparison.iloc[0]["total_return"] == pytest.approx(
        metrics["total_return"]
    )
    assert comparison.iloc[0]["annualized_return"] == pytest.approx(
        metrics["annualized_return"]
    )
    assert comparison.iloc[0]["sharpe_ratio"] == pytest.approx(
        metrics["sharpe_ratio"]
    )
    assert comparison.iloc[0]["max_drawdown"] == pytest.approx(
        metrics["max_drawdown"]
    )
    assert comparison.iloc[0]["volatility"] == pytest.approx(
        metrics["volatility"]
    )


def test_strategy_comparison_rejects_unsupported_result_type():
    with pytest.raises(
        TypeError,
        match="requires ExperimentResult",
    ):
        build_strategy_comparison(
            {"strategy_a": object()},
        )


def test_strategy_comparison_preserves_non_trusted_state():
    result = make_comparison_experiment_result(
        trust_state=DataTrustState.QUESTIONABLE,
        suitable=False,
        capability="backtest",
    )

    comparison = build_strategy_comparison(
        {"strategy_a": result},
    )

    row = comparison.iloc[0]

    assert row["data_trust_state"] == "questionable"
    assert row["data_trust_suitable"] is False
    assert row["data_trust_capability"] == "backtest"


def test_strategy_comparison_does_not_upgrade_trust_state():
    result = make_comparison_experiment_result(
        trust_state=DataTrustState.DEGRADED,
        suitable=False,
    )

    comparison = build_strategy_comparison(
        {"strategy_a": result},
    )

    row = comparison.iloc[0]

    assert row["data_trust_state"] == "degraded"
    assert row["data_trust_suitable"] is False