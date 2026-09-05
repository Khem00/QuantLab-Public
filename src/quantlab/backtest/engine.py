from __future__ import annotations

from typing import List

import pandas as pd

from quantlab.backtest.input_contract import validate_backtest_input
from quantlab.backtest.metrics import (
    annualized_return,
    maximum_drawdown,
    sharpe_ratio,
    total_return,
    volatility,
)
from quantlab.backtest.portfolio import Portfolio
from quantlab.backtest.result import BacktestResult
from quantlab.backtest.trades import Trade, TradeLog
from quantlab.data.trust import (
    DataTrustAssessment,
    DataTrustState,
    require_data_trust,
)


class BacktestEngine:
    """Chronological signal-based backtesting engine."""

    def __init__(
        self,
        initial_capital: float = 100000.0,
        commission: float = 0.0,
        slippage: float = 0.0,
        position_size: float = 1.0,
    ) -> None:
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage
        self.position_size = position_size
        self.portfolio = Portfolio(initial_capital=initial_capital)
        self.trade_log = TradeLog()
        self.equity_curve: pd.Series | None = None

    def run(
        self,
        data: pd.DataFrame,
        signals: pd.DataFrame,
        *,
        trust_assessment: DataTrustAssessment,
    ) -> BacktestResult:
        """
        Run the backtest and return the canonical BacktestResult.

        Signals are pre-indexed by (Date, Symbol), avoiding repeated
        DataFrame scans while preserving per-symbol chronological behavior.
        """
        data, signals = validate_backtest_input(data, signals)

        require_data_trust(
            trust_assessment,
            allowed_states={
                DataTrustState.TRUSTED,
                DataTrustState.CONDITIONALLY_TRUSTED,
            },
        )

        prices = data.sort_values(["Date", "Symbol"]).copy()
        signals = signals.sort_values(["Date", "Symbol"]).copy()

        signal_lookup = (
            signals
            .set_index(["Date", "Symbol"])["Signal"]
            .to_dict()
        )

        previous_date_by_symbol: dict[str, pd.Timestamp] = {}
        latest_prices: dict[str, float] = {}

        portfolio_series: List[float] = []

        for _, row in prices.iterrows():
            symbol = row["Symbol"]
            close = float(row["Close"])
            current_date = row["Date"]

            previous_date = previous_date_by_symbol.get(symbol)

            pending_signal = None

            if previous_date is not None:
                pending_signal = signal_lookup.get(
                    (previous_date, symbol)
                )

                if pending_signal is not None:
                    pending_signal = int(pending_signal)

            previous_date_by_symbol[symbol] = current_date

            current_position = self.portfolio.positions.get(
                symbol,
                0.0,
            )

            if pending_signal == 1 and current_position <= 0:
                execution_price = close * (1 + self.slippage)
                trade_cost = (
                    execution_price * self.position_size
                    + self.commission
                )

                self.portfolio.cash -= trade_cost
                self.portfolio.positions[symbol] = self.position_size

                self.trade_log.add_trade(
                    Trade(
                        timestamp=current_date,
                        symbol=symbol,
                        side="buy",
                        price=execution_price,
                        quantity=self.position_size,
                    )
                )

            elif pending_signal == -1 and current_position > 0:
                execution_price = close * (1 - self.slippage)
                trade_proceeds = (
                    execution_price * self.position_size
                    - self.commission
                )

                self.portfolio.cash += trade_proceeds
                self.portfolio.positions[symbol] = max(
                    0.0,
                    current_position - self.position_size,
                )

                self.trade_log.add_trade(
                    Trade(
                        timestamp=current_date,
                        symbol=symbol,
                        side="sell",
                        price=execution_price,
                        quantity=self.position_size,
                    )
                )

            latest_prices[symbol] = close

            portfolio_value = self.portfolio.update_value(
                pd.Series(latest_prices, dtype=float)
            )

            portfolio_series.append(portfolio_value)

        values = pd.Series(
            portfolio_series,
            dtype=float,
        )

        self.equity_curve = values

        metrics = {
            "total_return": total_return(values),
            "annualized_return": annualized_return(values),
            "sharpe_ratio": sharpe_ratio(values),
            "max_drawdown": maximum_drawdown(values),
            "volatility": volatility(values),
        }

        return BacktestResult(
            metrics=metrics,
            equity_curve=values,
            trade_log=self.trade_log,
            data_trust=trust_assessment,
        )
