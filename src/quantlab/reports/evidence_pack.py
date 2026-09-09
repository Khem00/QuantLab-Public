from __future__ import annotations

import hashlib
import json
import shutil
from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from quantlab.experiments.result import ExperimentResult


PACK_VERSION = "1.0"


def _json_safe(value: Any) -> Any:
    if is_dataclass(value):
        return _json_safe(asdict(value))
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]
    if hasattr(value, "value"):
        return value.value
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, (pd.Timestamp, datetime)):
        return value.isoformat()
    return value


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_trades(result: ExperimentResult, path: Path) -> None:
    rows = [
        {
            "timestamp": trade.timestamp,
            "symbol": trade.symbol,
            "side": trade.side,
            "price": trade.price,
            "quantity": trade.quantity,
        }
        for trade in result.backtest.trade_log.trades
    ]
    pd.DataFrame(rows).to_csv(path, index=False)


def _trade_event_statistics(result: ExperimentResult) -> dict[str, int]:
    """Summarize trade events, completed trades, and unmatched open positions."""
    positions: dict[str, float] = {}

    for trade in result.backtest.trade_log.trades:
        if trade.side == "buy":
            positions[trade.symbol] = (
                positions.get(trade.symbol, 0.0) + trade.quantity
            )
        elif trade.side == "sell":
            remaining = positions.get(trade.symbol, 0.0) - trade.quantity
            if remaining > 0:
                positions[trade.symbol] = remaining
            else:
                positions.pop(trade.symbol, None)

    return {
        "trade_events": len(result.backtest.trade_log.trades),
        "completed_trades": int(
            result.trade_statistics.get("total_trades", 0)
        ),
        "open_positions": len(positions),
    }


def _dataset_metadata(result: ExperimentResult) -> dict[str, Any]:
    processed = result.artifacts.processed_data_path

    if processed is None:
        return {}

    processed = Path(processed)
    csv_files = (
        list(processed.glob("*.csv"))
        if processed.is_dir()
        else [processed]
    )

    metadata: dict[str, Any] = {"files": []}

    for csv_path in csv_files:
        try:
            frame = pd.read_csv(csv_path)

            item = {
                "filename": csv_path.name,
                "rows": len(frame),
                "columns": list(frame.columns),
            }

            if "Date" in frame.columns and len(frame):
                item["start_date"] = str(frame["Date"].iloc[0])
                item["end_date"] = str(frame["Date"].iloc[-1])

            if "Symbol" in frame.columns:
                item["symbols"] = sorted(
                    frame["Symbol"].dropna().astype(str).unique().tolist()
                )

            metadata["files"].append(item)

        except Exception as exc:
            metadata["files"].append(
                {
                    "filename": csv_path.name,
                    "read_error": str(exc),
                }
            )

    return metadata


def _copy_artifact(
    source: Path,
    output: Path,
    relative_path: Path,
) -> Path:
    """Copy one artifact into the pack and return its destination."""
    destination = output / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)

    # The experiment runner may already have written the artifact
    # directly into the Evidence Pack directory.
    if source.resolve() != destination.resolve():
        shutil.copy2(source, destination)

    return destination


def _collect_artifacts(
    result: ExperimentResult,
    output: Path,
) -> list[Path]:
    """Copy experiment artifacts into the pack and return destinations."""
    destinations: list[Path] = []

    candidates = [
        (
            result.artifacts.summary_path,
            Path("experiment_summary.csv"),
        ),
        (
            result.artifacts.equity_curve_path,
            Path("equity_curve.csv"),
        ),
    ]

    for source, relative_path in candidates:
        if source is None:
            continue

        source_path = Path(source)

        if not source_path.exists() or not source_path.is_file():
            continue

        destinations.append(
            _copy_artifact(
                source_path,
                output,
                relative_path,
            )
        )

    processed = result.artifacts.processed_data_path

    if processed is not None:
        processed_path = Path(processed)

        if processed_path.is_dir():
            for source_path in sorted(processed_path.glob("*.csv")):
                destinations.append(
                    _copy_artifact(
                        source_path,
                        output,
                        Path("processed") / source_path.name,
                    )
                )
        elif processed_path.is_file():
            destinations.append(
                _copy_artifact(
                    processed_path,
                    output,
                    Path("processed") / processed_path.name,
                )
            )

    return destinations


def _write_report(
    result: ExperimentResult,
    manifest: dict[str, Any],
    path: Path,
) -> None:
    metrics = result.metrics
    stats = result.trade_statistics
    trade_events = _trade_event_statistics(result)
    trust = _json_safe(result.data_trust)

    lines = [
        "# QuantLab Backtest Evidence Pack",
        "",
        f"**Pack version:** {PACK_VERSION}",
        f"**Generated:** {manifest['generated_at']}",
        "",
        "## Executive Result",
        "",
        f"- **Status:** {result.status}",
        f"- **Dataset:** {result.dataset_name}",
        f"- **Strategy:** {result.strategy_name}",
        f"- **Total return:** {metrics.get('total_return')}",
        f"- **Sharpe ratio:** {metrics.get('sharpe_ratio')}",
        f"- **Maximum drawdown:** {metrics.get('max_drawdown')}",
        "",
        "## Experiment Configuration",
        "",
        f"- Initial capital: {result.configuration.initial_capital}",
        f"- Commission: {result.configuration.commission}",
        f"- Slippage: {result.configuration.slippage}",
        f"- Position size: {result.configuration.position_size}",
        "",
        "## Data Trust",
        "",
        "```json",
        json.dumps(trust, indent=2, default=str),
        "```",
        "",
        "## Performance Metrics",
        "",
        "| Metric | Value |",
        "|---|---:|",
    ]

    for key, value in metrics.items():
        lines.append(f"| {key} | {value} |")

    lines += [
        "",
        "## Trade Activity",
        "",
        "| Measure | Value |",
        "|---|---:|",
        f"| Trade events | {trade_events['trade_events']} |",
        f"| Completed trades | {trade_events['completed_trades']} |",
        f"| Open positions | {trade_events['open_positions']} |",
        "",
        "## Completed Trade Statistics",
        "",
        "| Statistic | Value |",
        "|---|---:|",
    ]

    for key, value in stats.items():
        lines.append(f"| {key} | {value} |")

    lines += [
        "",
        "## Evidence Inventory",
        "",
    ]

    for item in manifest["artifacts"]:
        lines.append(
            f"- `{item['path']}` — SHA-256 `{item['sha256']}`"
        )

    lines += [
        "",
        "The SHA-256 for `report.md` is recorded in `manifest.json`; the report does not include its own hash.",
        "",
        "## Reproducibility",
        "",
        "This pack preserves the principal outputs needed to inspect the completed experiment, including processed data, the realized equity curve, trade events, configuration, metrics, and cryptographic hashes.",
        "",
        "## Limitations",
        "",
        "- This is a research/audit evidence artifact, not investment advice.",
        "- Results depend on the supplied historical dataset and strategy configuration.",
        "- Completed trade statistics describe buy-to-sell pairs; an open position at the end of the run is reported separately and is not counted as a completed trade.",
        "- This pack does not represent live execution or guarantee future performance.",
        "",
    ]

    path.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )


def build_evidence_pack(
    result: ExperimentResult,
    output_dir: str | Path,
) -> Path:
    """Build a self-contained, buyer-readable evidence pack."""
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    trades_path = output / "trades.csv"
    _write_trades(result, trades_path)

    copied_artifacts = _collect_artifacts(
        result,
        output,
    )

    artifact_paths = [
        *copied_artifacts,
        trades_path,
    ]

    artifacts: list[dict[str, str]] = []

    for path in artifact_paths:
        relative = path.relative_to(output)

        artifacts.append(
            {
                "path": str(relative).replace("\\", "/"),
                "sha256": _sha256(path),
            }
        )

    manifest_path = output / "manifest.json"
    report_path = output / "report.md"

    manifest: dict[str, Any] = {
        "pack_version": PACK_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": result.status,
        "dataset": {
            "name": result.dataset_name,
            "metadata": _dataset_metadata(result),
        },
        "strategy": {
            "name": result.strategy_name,
        },
        "configuration": _json_safe(result.configuration),
        "data_trust": _json_safe(result.data_trust),
        "metrics": _json_safe(result.metrics),
        "trade_statistics": _json_safe(result.trade_statistics),
        "trade_activity": _trade_event_statistics(result),
        "artifacts": artifacts,
        "limitations": [
            "Research/audit output only; not investment advice.",
            "Historical backtest results do not guarantee future performance.",
            "Completed trade statistics exclude any position still open at the end of the run.",
        ],
    }

    _write_report(
        result,
        manifest,
        report_path,
    )

    artifacts.append(
        {
            "path": "report.md",
            "sha256": _sha256(report_path),
        }
    )

    manifest["artifacts"] = artifacts

    manifest_path.write_text(
        json.dumps(
            manifest,
            indent=2,
            default=str,
        ) + "\n",
        encoding="utf-8",
    )

    return output
