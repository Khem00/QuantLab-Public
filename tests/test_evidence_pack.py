from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd

from quantlab.backtest.result import BacktestResult
from quantlab.backtest.trades import Trade, TradeLog
from quantlab.data.trust import DataTrustAssessment, DataTrustState
from quantlab.experiments.config import ExperimentConfig
from quantlab.experiments.result import ExperimentArtifacts, ExperimentResult
from quantlab.reports.evidence_pack import build_evidence_pack


def make_result(tmp_path: Path) -> ExperimentResult:
    equity_curve = pd.Series(
        [100000.0, 100100.0, 100300.0],
        index=pd.date_range(
            "2024-01-01",
            periods=3,
            freq="D",
        ),
    )

    trade_log = TradeLog(
        trades=[
            Trade(
                timestamp=pd.Timestamp("2024-01-02"),
                symbol="TEST",
                side="buy",
                price=100.0,
                quantity=1.0,
            ),
        ]
    )

    backtest = BacktestResult(
        metrics={
            "total_return": 0.003,
            "annualized_return": 0.5,
            "sharpe_ratio": 1.2,
            "max_drawdown": -0.01,
            "volatility": 0.1,
        },
        equity_curve=equity_curve,
        trade_log=trade_log,
        data_trust=DataTrustAssessment(
            state=DataTrustState.TRUSTED,
            capability="backtest",
            suitable=True,
            evidence=("test-data.csv",),
        ),
    )

    processed_dir = tmp_path / "processed"
    processed_dir.mkdir()

    pd.DataFrame(
        {
            "Date": pd.date_range(
                "2024-01-01",
                periods=3,
                freq="D",
            ),
            "Symbol": ["TEST"] * 3,
            "Close": [100.0, 101.0, 103.0],
        }
    ).to_csv(
        processed_dir / "TEST.csv",
        index=False,
    )

    summary_path = tmp_path / "experiment_summary.csv"
    pd.DataFrame(
        {
            "total_return": [0.003],
            "sharpe_ratio": [1.2],
        },
        index=["portfolio"],
    ).to_csv(summary_path)

    equity_path = tmp_path / "equity_curve.csv"
    equity_curve.to_csv(
        equity_path,
        header=["Portfolio_Value"],
    )

    return ExperimentResult(
        status="completed",
        dataset_name="TEST",
        strategy_name="buy_hold",
        configuration=ExperimentConfig(
            dataset_name="TEST",
            strategy_name="buy_hold",
            source_quality=DataTrustState.TRUSTED,
            output_dir=tmp_path,
        ),
        backtest=backtest,
        trade_statistics={
            "total_trades": 0,
            "winning_trades": 0,
            "losing_trades": 0,
            "win_rate": 0.0,
            "average_win": 0.0,
            "average_loss": 0.0,
            "profit_factor": 0.0,
        },
        artifacts=ExperimentArtifacts(
            summary_path=summary_path,
            equity_curve_path=equity_path,
            processed_data_path=processed_dir,
        ),
    )


def test_build_evidence_pack_creates_expected_files(tmp_path):
    result = make_result(tmp_path)
    output = tmp_path / "pack"

    build_evidence_pack(result, output)

    assert (output / "manifest.json").exists()
    assert (output / "report.md").exists()
    assert (output / "trades.csv").exists()
    assert (output / "experiment_summary.csv").exists()
    assert (output / "equity_curve.csv").exists()
    assert (output / "processed" / "TEST.csv").exists()


def test_manifest_records_trade_activity_and_hashes(tmp_path):
    result = make_result(tmp_path)
    output = tmp_path / "pack"

    build_evidence_pack(result, output)

    manifest = json.loads(
        (output / "manifest.json").read_text(
            encoding="utf-8"
        )
    )

    assert manifest["trade_activity"] == {
        "trade_events": 1,
        "completed_trades": 0,
        "open_positions": 1,
    }

    for artifact in manifest["artifacts"]:
        artifact_path = output / artifact["path"]
        assert artifact_path.exists()
        assert artifact["sha256"] == hashlib.sha256(
            artifact_path.read_bytes()
        ).hexdigest()


def test_report_distinguishes_open_position_from_completed_trades(
    tmp_path,
):
    result = make_result(tmp_path)
    output = tmp_path / "pack"

    build_evidence_pack(result, output)

    report = (output / "report.md").read_text(
        encoding="utf-8"
    )

    assert "## Trade Activity" in report
    assert "| Trade events | 1 |" in report
    assert "| Completed trades | 0 |" in report
    assert "| Open positions | 1 |" in report
    assert "## Completed Trade Statistics" in report
    assert "The SHA-256 for `report.md` is recorded in `manifest.json`" in report


def test_trades_csv_contains_realized_trade_events(tmp_path):
    result = make_result(tmp_path)
    output = tmp_path / "pack"

    build_evidence_pack(result, output)

    trades = pd.read_csv(output / "trades.csv")

    assert len(trades) == 1
    assert trades.iloc[0]["symbol"] == "TEST"
    assert trades.iloc[0]["side"] == "buy"
    assert trades.iloc[0]["quantity"] == 1.0
