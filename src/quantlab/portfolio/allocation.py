from __future__ import annotations

import pandas as pd


def equal_weight_allocation(assets: list[str]) -> pd.Series:
    """Return equal weights for a list of assets."""
    if not assets:
        return pd.Series(dtype=float)
    weights = 1 / len(assets)
    return pd.Series([weights] * len(assets), index=assets, dtype=float)


def weight_portfolio(values: pd.Series) -> pd.Series:
    """Normalize a series of weights to sum to 1.0."""
    if values.empty:
        return pd.Series(dtype=float)
    total = values.sum()
    if total == 0:
        return pd.Series(0.0, index=values.index)
    return values / total
