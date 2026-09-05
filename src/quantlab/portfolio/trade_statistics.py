from __future__ import annotations

from typing import Any

from quantlab.backtest.trades import TradeLog


def calculate_trade_statistics(
    trade_log: TradeLog,
) -> dict[str, Any]:
    """
    Calculate trade performance statistics from completed trades.
    """

    if not trade_log.trades:
        return {
            "total_trades": 0,
            "winning_trades": 0,
            "losing_trades": 0,
            "win_rate": 0.0,
            "average_win": 0.0,
            "average_loss": 0.0,
            "profit_factor": 0.0,
        }

    positions = {}
    profits = []

    for trade in trade_log.trades:

        if trade.side == "buy":
            positions[trade.symbol] = trade.price

        elif trade.side == "sell":

            entry_price = positions.get(trade.symbol)

            if entry_price is not None:
                profit = (
                    trade.price - entry_price
                ) * trade.quantity

                profits.append(profit)

                del positions[trade.symbol]

    if not profits:
        return {
            "total_trades": 0,
            "winning_trades": 0,
            "losing_trades": 0,
            "win_rate": 0.0,
            "average_win": 0.0,
            "average_loss": 0.0,
            "profit_factor": 0.0,
        }

    winning = [
        p for p in profits
        if p > 0
    ]

    losing = [
        p for p in profits
        if p < 0
    ]

    total_trades = len(profits)

    average_win = (
        sum(winning) / len(winning)
        if winning
        else 0.0
    )

    average_loss = (
        sum(losing) / len(losing)
        if losing
        else 0.0
    )

    gross_profit = sum(winning)

    gross_loss = abs(sum(losing))

    profit_factor = (
        gross_profit / gross_loss
        if gross_loss > 0
        else 0.0
    )

    return {
        "total_trades": total_trades,
        "winning_trades": len(winning),
        "losing_trades": len(losing),
        "win_rate": len(winning) / total_trades,
        "average_win": average_win,
        "average_loss": average_loss,
        "profit_factor": profit_factor,
    }