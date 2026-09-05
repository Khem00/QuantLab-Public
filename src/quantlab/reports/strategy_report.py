from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


def generate_strategy_report(
    comparison: pd.DataFrame,
    output_path: str | Path,
    results: dict[str, Any] | None = None,
) -> Path:
    """
    Generate a Markdown research report from strategy comparison results.

    Optionally includes trade statistics from ExperimentResult objects.
    """

    path = Path(output_path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    ranked = comparison.sort_values(
        by="sharpe_ratio",
        ascending=False,
    )

    lines = []

    lines.append(
        "# QuantLab Strategy Comparison Report\n"
    )

    lines.append(
        "## Performance Ranking\n"
    )

    lines.append(
        ranked.to_markdown()
    )

    if results:

        lines.append(
            "\n## Trade Statistics\n"
        )

        for strategy_name, result in results.items():

            trade_stats = getattr(
                result,
                "trade_statistics",
                None,
            )

            if trade_stats is None:
                continue

            lines.append(
                f"\n### {strategy_name}\n"
            )

            lines.append(
                f"- Total trades: {trade_stats.get('total_trades', 0)}"
            )

            lines.append(
                f"- Winning trades: {trade_stats.get('winning_trades', 0)}"
            )

            lines.append(
                f"- Losing trades: {trade_stats.get('losing_trades', 0)}"
            )

            lines.append(
                f"- Win rate: {trade_stats.get('win_rate', 0.0):.2%}"
            )

            lines.append(
                f"- Average win: {trade_stats.get('average_win', 0.0):.2f}"
            )

            lines.append(
                f"- Average loss: {trade_stats.get('average_loss', 0.0):.2f}"
            )

            lines.append(
                f"- Profit factor: {trade_stats.get('profit_factor', 0.0):.2f}"
            )

    lines.append(
        "\n## Summary\n"
    )

    best_strategy = ranked.iloc[0]["strategy"]

    lines.append(
        f"Best risk-adjusted performer: **{best_strategy}** "
        "based on Sharpe ratio.\n"
    )

    path.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )

    return path