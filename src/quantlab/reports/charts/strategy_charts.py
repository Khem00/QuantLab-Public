from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def create_strategy_charts(
    comparison: pd.DataFrame,
    output_dir: str | Path,
) -> list[Path]:
    """
    Create visual comparison charts for strategy performance.
    """

    output_path = Path(output_dir)
    output_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    charts = []

    metrics = [
        ("total_return", "Strategy Returns", "strategy_returns.png"),
        ("sharpe_ratio", "Sharpe Ratio Comparison", "sharpe_ratio.png"),
        ("max_drawdown", "Maximum Drawdown", "drawdown.png"),
        ("volatility", "Volatility Comparison", "volatility.png"),
    ]

    for column, title, filename in metrics:

        plt.figure(figsize=(8, 5))

        plt.bar(
            comparison["strategy"],
            comparison[column],
        )

        plt.title(title)
        plt.xlabel("Strategy")
        plt.ylabel(column)

        plt.xticks(
            rotation=45,
            ha="right",
        )

        plt.tight_layout()

        file_path = output_path / filename

        plt.savefig(
            file_path,
            dpi=300,
            bbox_inches="tight",
        )

        plt.close()

        charts.append(file_path)

    return charts