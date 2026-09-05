from __future__ import annotations

import pandas as pd

from quantlab.experiments.result import ExperimentResult


def build_strategy_comparison(
    results: dict[str, ExperimentResult],
) -> pd.DataFrame:
    """
    Build an analytical comparison projection from canonical experiment results.

    Financial metrics and Data Trust metadata are projected directly from the
    canonical ExperimentResult -> BacktestResult boundary.

    This function does not calculate, reconstruct, upgrade, or discard
    authoritative financial metrics or Data Trust state.
    """

    rows = []

    for strategy_name, result in results.items():
        if not isinstance(result, ExperimentResult):
            raise TypeError(
                "Strategy comparison requires ExperimentResult inputs; "
                f"received {type(result).__name__}"
            )

        # Explicit canonical-result boundary.
        backtest = result.backtest
        metrics = backtest.metrics
        data_trust = backtest.data_trust

        rows.append(
            {
                "strategy": strategy_name,
                "total_return": metrics.get("total_return"),
                "annualized_return": metrics.get("annualized_return"),
                "sharpe_ratio": metrics.get("sharpe_ratio"),
                "max_drawdown": metrics.get("max_drawdown"),
                "volatility": metrics.get("volatility"),
                "data_trust_state": data_trust.state.value,
                "data_trust_suitable": bool(data_trust.suitable),
                "data_trust_capability": data_trust.capability,
            }
        )

    comparison = pd.DataFrame(rows)

    if comparison.empty:
        return comparison

    # Keep the projection contract's suitability values as ordinary Python
    # bool objects rather than NumPy boolean scalars.
    comparison["data_trust_suitable"] = (
        comparison["data_trust_suitable"]
        .map(bool)
        .astype(object)
    )

    comparison = comparison.sort_values(
        by="sharpe_ratio",
        ascending=False,
    )

    comparison.reset_index(
        drop=True,
        inplace=True,
    )

    return comparison
