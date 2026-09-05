from __future__ import annotations

from typing import Dict, Type

from quantlab.strategies.base import BaseStrategy
from quantlab.strategies.buy_hold import BuyHoldStrategy
from quantlab.strategies.rsi_strategy import RsiStrategy
from quantlab.strategies.sma_cross import SmaCrossStrategy


_STRATEGY_REGISTRY: Dict[str, Type[BaseStrategy]] = {
    "buy_hold": BuyHoldStrategy,
    "rsi": RsiStrategy,
    "sma_cross": SmaCrossStrategy,
}


def get_strategy(strategy_name: str) -> BaseStrategy:
    """
    Return a strategy instance from the registry.
    """

    normalized_name = strategy_name.strip().lower()

    strategy_cls = _STRATEGY_REGISTRY.get(normalized_name)

    if strategy_cls is None:
        raise ValueError(
            f"Unknown strategy: {strategy_name}"
        )

    return strategy_cls()


def list_strategies() -> list[str]:
    """
    Return all available strategy names.
    """

    return sorted(_STRATEGY_REGISTRY.keys())