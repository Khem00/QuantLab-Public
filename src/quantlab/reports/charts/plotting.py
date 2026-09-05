from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def plot_equity_curve(
    equity_curve: pd.Series,
    *,
    ax=None,
):
    """Plot portfolio equity over time and return the matplotlib Axes."""
    series = pd.Series(equity_curve).dropna()

    if series.empty:
        raise ValueError("equity_curve must contain at least one valid observation.")

    if ax is None:
        _, ax = plt.subplots()

    ax.plot(series.index, series.values)
    ax.set_title("Equity Curve")
    ax.set_xlabel("Date")
    ax.set_ylabel("Equity")
    ax.grid(True, alpha=0.25)

    return ax


def plot_cumulative_returns(
    returns: pd.Series,
    *,
    ax=None,
):
    """Plot cumulative returns from periodic returns."""
    series = pd.Series(returns).dropna()

    if series.empty:
        raise ValueError("returns must contain at least one valid observation.")

    if ax is None:
        _, ax = plt.subplots()

    cumulative = (1.0 + series).cumprod() - 1.0

    ax.plot(cumulative.index, cumulative.values)
    ax.set_title("Cumulative Returns")
    ax.set_xlabel("Date")
    ax.set_ylabel("Cumulative Return")
    ax.grid(True, alpha=0.25)

    return ax


def plot_drawdown(
    equity_curve: pd.Series,
    *,
    ax=None,
):
    """Plot portfolio drawdown from an equity curve."""
    series = pd.Series(equity_curve).dropna()

    if series.empty:
        raise ValueError("equity_curve must contain at least one valid observation.")

    if (series <= 0).any():
        raise ValueError("equity_curve must contain strictly positive values.")

    if ax is None:
        _, ax = plt.subplots()

    running_peak = series.cummax()
    drawdown = series / running_peak - 1.0

    ax.plot(drawdown.index, drawdown.values)
    ax.set_title("Drawdown")
    ax.set_xlabel("Date")
    ax.set_ylabel("Drawdown")
    ax.grid(True, alpha=0.25)

    return ax


def plot_strategy_comparison(
    strategies: Mapping[str, pd.Series],
    *,
    ax=None,
):
    """Plot multiple strategy equity/return series for comparison."""
    if not strategies:
        raise ValueError("strategies must contain at least one strategy.")

    if ax is None:
        _, ax = plt.subplots()

    for name, series in strategies.items():
        values = pd.Series(series).dropna()

        if values.empty:
            raise ValueError(
                f"Strategy '{name}' must contain at least one valid observation."
            )

        ax.plot(values.index, values.values, label=name)

    ax.set_title("Strategy Comparison")
    ax.set_xlabel("Date")
    ax.set_ylabel("Value")
    ax.legend()
    ax.grid(True, alpha=0.25)

    return ax


def save_chart(
    ax,
    output_path: str | Path,
    *,
    dpi: int = 300,
) -> Path:
    """Save a chart and return its output path."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    ax.figure.tight_layout()
    ax.figure.savefig(path, dpi=dpi, bbox_inches="tight")

    return path
