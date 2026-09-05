from __future__ import annotations

from typing import Any

import pandas as pd

from quantlab.backtest.result import BacktestResult
from quantlab.portfolio.risk import maximum_drawdown, sharpe_ratio, volatility
from quantlab.portfolio.returns import (
    cumulative_returns,
    equity_curve,
    portfolio_returns,
)


def _extract_equity_curve(payload: Any) -> pd.Series:
    if isinstance(payload, BacktestResult):
        return payload.equity_curve.astype(float)

    if isinstance(payload, pd.Series):
        return payload.astype(float)

    if isinstance(payload, pd.DataFrame):
        returns = portfolio_returns(payload)
        cum_returns = cumulative_returns(returns)
        return equity_curve(cum_returns)

    raise TypeError(
        "Unsupported summary input type"
    )


def _extract_metrics(payload: Any) -> dict[str, float]:
    if isinstance(payload, BacktestResult):
        return {
            key: float(value)
            for key, value in payload.metrics.items()
            if isinstance(value, (int, float))
        }

    return {}


def _build_summary_from_equity(
    equity: pd.Series,
    metrics: dict[str, float],
    index_label: str,
) -> pd.DataFrame:
    if not equity.empty:
        total_return = (
            float((equity.iloc[-1] / equity.iloc[0]) - 1)
            if equity.iloc[0] != 0
            else 0.0
        )

        drawdown = maximum_drawdown(equity)

        returns = pd.Series(
            equity.pct_change().dropna()
        )

        vol = volatility(returns)
        sharpe = sharpe_ratio(returns)

    else:
        total_return = 0.0
        drawdown = 0.0
        vol = 0.0
        sharpe = 0.0

    if metrics:
        total_return = metrics.get(
            "total_return",
            total_return,
        )

        vol = metrics.get(
            "volatility",
            vol,
        )

        sharpe = metrics.get(
            "sharpe_ratio",
            sharpe,
        )

        drawdown = metrics.get(
            "max_drawdown",
            drawdown,
        )

    return pd.DataFrame(
        {
            "total_return": [total_return],
            "volatility": [vol],
            "sharpe_ratio": [sharpe],
            "max_drawdown": [drawdown],
        },
        index=[index_label],
    )


def build_summary(
    payload: BacktestResult | pd.Series | pd.DataFrame,
) -> pd.DataFrame:
    """
    Build a performance summary.

    Canonical backtest input:
        BacktestResult

    Raw analytical inputs remain supported:
        pd.Series
        pd.DataFrame

    For BacktestResult, canonical metrics are projected directly from
    the result rather than reconstructed from the equity curve.
    """
    if isinstance(payload, BacktestResult):
        metrics = _extract_metrics(payload)

        return pd.DataFrame(
            {
                "total_return": [metrics.get("total_return", 0.0)],
                "volatility": [metrics.get("volatility", 0.0)],
                "sharpe_ratio": [metrics.get("sharpe_ratio", 0.0)],
                "max_drawdown": [metrics.get("max_drawdown", 0.0)],
            },
            index=["portfolio"],
        )

    equity = _extract_equity_curve(payload)

    return _build_summary_from_equity(
        equity,
        {},
        "portfolio",
    )


def build_benchmark_summary(
    prices: pd.Series | pd.DataFrame,
    initial_capital: float = 100000.0,
) -> pd.DataFrame:
    """Create a buy-and-hold benchmark summary."""

    if isinstance(prices, pd.DataFrame):
        if prices.empty:
            equity = pd.Series(dtype=float)
        else:
            price_series = prices.iloc[:, 0].astype(float)
            equity = _build_benchmark_equity_curve(
                price_series,
                initial_capital,
            )

    elif isinstance(prices, pd.Series):
        equity = _build_benchmark_equity_curve(
            prices.astype(float),
            initial_capital,
        )

    else:
        raise TypeError(
            "Unsupported benchmark input type"
        )

    return _build_summary_from_equity(
        equity,
        {},
        "benchmark",
    )


def _build_benchmark_equity_curve(
    prices: pd.Series,
    initial_capital: float,
) -> pd.Series:
    if prices.empty:
        return pd.Series(dtype=float)

    first_price = float(prices.iloc[0])

    if first_price == 0:
        return pd.Series(
            [float(initial_capital)] * len(prices),
            index=prices.index,
            dtype=float,
        )

    return pd.Series(
        initial_capital * (prices / first_price),
        index=prices.index,
        dtype=float,
    )


def build_comparison_summary(
    strategy_result: BacktestResult,
    benchmark_prices: pd.Series | pd.DataFrame,
    initial_capital: float = 100000.0,
    strategy_label: str = "strategy",
    benchmark_label: str = "benchmark",
) -> pd.DataFrame:
    """
    Build a comparison table containing a canonical backtest
    summary and a buy-and-hold benchmark summary.
    """
    if not isinstance(
        strategy_result,
        BacktestResult,
    ):
        raise TypeError(
            "strategy_result must be a BacktestResult"
        )

    strategy_summary = build_summary(
        strategy_result
    )

    strategy_summary.index = [
        strategy_label
    ]

    benchmark_summary = build_benchmark_summary(
        benchmark_prices,
        initial_capital=initial_capital,
    )

    benchmark_summary.index = [
        benchmark_label
    ]

    return pd.concat(
        [
            strategy_summary,
            benchmark_summary,
        ],
        axis=0,
    )


def compare_summaries(
    summary_map: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """Combine multiple strategy summaries into one comparison table."""
    return pd.concat(
        summary_map,
        axis=0,
    )
