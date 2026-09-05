from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from quantlab.backtest.engine import BacktestEngine
from quantlab.experiments.config import ExperimentConfig
from quantlab.backtest.metrics import annualized_return, maximum_drawdown, sharpe_ratio, total_return, volatility
from quantlab.backtest.portfolio import Portfolio
from quantlab.backtest.trades import Trade, TradeLog
from quantlab.data.trust import DataTrustState, assess_data_trust


def trusted_backtest_assessment():
    return assess_data_trust(
        capability="backtest",
        validation_passed=True,
        source_quality=DataTrustState.TRUSTED,
    )


def make_sample_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    dates = pd.date_range("2024-01-01", periods=4, freq="D")
    data = pd.DataFrame(
        {
            "Date": dates,
            "Symbol": ["TEST"] * 4,
            "Close": [100.0, 101.0, 102.0, 103.0],
        }
    )
    signals = pd.DataFrame(
        {
            "Date": dates,
            "Symbol": ["TEST"] * 4,
            "Signal": [0, 1, 0, -1],
        }
    )
    return data, signals


def test_portfolio_updates_value():
    portfolio = Portfolio(initial_capital=1000.0)
    prices = pd.Series([100.0, 101.0], index=["TEST", "TEST"])
    assert portfolio.update_value(prices) == 1000.0


def test_trade_log_can_store_trades():
    trade_log = TradeLog()
    trade_log.add_trade(Trade(timestamp=pd.Timestamp("2024-01-01"), symbol="TEST", side="buy", price=100.0, quantity=1.0))
    assert len(trade_log.trades) == 1


def test_metrics_return_numeric_values():
    values = pd.Series([100.0, 110.0, 90.0], dtype=float)
    assert np.isfinite(total_return(values))
    assert np.isfinite(annualized_return(values))
    assert np.isfinite(sharpe_ratio(values))
    assert np.isfinite(maximum_drawdown(values))
    assert np.isfinite(volatility(values))


def test_backtest_engine_runs():
    data, signals = make_sample_data()
    engine = BacktestEngine(initial_capital=1000.0)
    result = engine.run(
        data,
        signals,
        trust_assessment=trusted_backtest_assessment(),
    )
    assert result.metrics["total_return"] > 0.0
    assert np.isfinite(result.metrics["annualized_return"])
    assert np.isfinite(result.metrics["sharpe_ratio"])
    assert np.isfinite(result.metrics["max_drawdown"])
    assert np.isfinite(result.metrics["volatility"])


def test_backtest_uses_only_current_bar_prices_for_valuation():
    data = pd.DataFrame(
        {
            "Date": pd.date_range("2024-01-01", periods=3, freq="D"),
            "Symbol": ["TEST"] * 3,
            "Close": [100.0, 110.0, 120.0],
        }
    )
    signals = pd.DataFrame(
        {
            "Date": data["Date"],
            "Symbol": ["TEST"] * 3,
            "Signal": [1, 0, 0],
        }
    )

    engine = BacktestEngine(initial_capital=1000.0)
    engine.run(data, signals, trust_assessment=trusted_backtest_assessment())

    assert engine.portfolio.cash == 890.0
    assert engine.portfolio.positions["TEST"] == 1.0
    assert engine.portfolio.update_value(pd.Series([110.0], index=["TEST"])) == 1000.0


def test_backtest_executes_signals_on_next_bar():
    data = pd.DataFrame(
        {
            "Date": pd.date_range("2024-01-01", periods=3, freq="D"),
            "Symbol": ["TEST"] * 3,
            "Close": [100.0, 110.0, 120.0],
        }
    )
    signals = pd.DataFrame(
        {
            "Date": data["Date"],
            "Symbol": ["TEST"] * 3,
            "Signal": [1, 0, 0],
        }
    )

    engine = BacktestEngine(initial_capital=1000.0)
    engine.run(data, signals, trust_assessment=trusted_backtest_assessment())

    assert engine.trade_log.trades[0].price == 110.0
    assert engine.trade_log.trades[0].timestamp == data["Date"].iloc[1]


def test_experiment_config_rejects_negative_commission() -> None:
    try:
        ExperimentConfig(dataset_name="AAPL_history", strategy_name="buy_hold", source_quality=DataTrustState.TRUSTED, commission=-0.01)
    except ValueError as exc:
        assert "commission" in str(exc)
    else:
        raise AssertionError("Expected ValueError for negative commission")


def test_experiment_config_rejects_negative_slippage() -> None:
    try:
        ExperimentConfig(dataset_name="AAPL_history", strategy_name="buy_hold", source_quality=DataTrustState.TRUSTED, slippage=-0.01)
    except ValueError as exc:
        assert "slippage" in str(exc)
    else:
        raise AssertionError("Expected ValueError for negative slippage")


def test_backtest_applies_commission_to_trade_execution():
    data = pd.DataFrame(
        {
            "Date": pd.date_range("2024-01-01", periods=2, freq="D"),
            "Symbol": ["TEST"] * 2,
            "Close": [100.0, 110.0],
        }
    )
    signals = pd.DataFrame(
        {
            "Date": data["Date"],
            "Symbol": ["TEST"] * 2,
            "Signal": [1, 0],
        }
    )

    engine = BacktestEngine(initial_capital=1000.0, commission=1.0)
    engine.run(data, signals, trust_assessment=trusted_backtest_assessment())

    assert engine.portfolio.cash == 889.0


def test_backtest_applies_slippage_to_execution_price_and_cash():
    data = pd.DataFrame(
        {
            "Date": pd.date_range("2024-01-01", periods=2, freq="D"),
            "Symbol": ["TEST"] * 2,
            "Close": [100.0, 110.0],
        }
    )
    signals = pd.DataFrame(
        {
            "Date": data["Date"],
            "Symbol": ["TEST"] * 2,
            "Signal": [1, 0],
        }
    )

    engine = BacktestEngine(initial_capital=1000.0, slippage=0.01)
    engine.run(data, signals, trust_assessment=trusted_backtest_assessment())

    assert engine.trade_log.trades[0].price == 111.1
    assert engine.portfolio.cash == 888.9


def test_experiment_config_rejects_non_positive_position_size() -> None:
    try:
        ExperimentConfig(dataset_name="AAPL_history", strategy_name="buy_hold", source_quality=DataTrustState.TRUSTED, position_size=0.0)
    except ValueError as exc:
        assert "position_size" in str(exc)
    else:
        raise AssertionError("Expected ValueError for non-positive position size")


def test_backtest_uses_position_size_for_exposure_and_cash():
    data = pd.DataFrame(
        {
            "Date": pd.date_range("2024-01-01", periods=2, freq="D"),
            "Symbol": ["TEST"] * 2,
            "Close": [100.0, 110.0],
        }
    )
    signals = pd.DataFrame(
        {
            "Date": data["Date"],
            "Symbol": ["TEST"] * 2,
            "Signal": [1, 0],
        }
    )

    engine = BacktestEngine(initial_capital=1000.0, position_size=0.5)
    engine.run(data, signals, trust_assessment=trusted_backtest_assessment())

    assert engine.portfolio.positions["TEST"] == 0.5
    assert engine.portfolio.cash == 945.0

def test_backtest_does_not_repeatedly_buy_when_already_long():
    data = pd.DataFrame(
        {
            "Date": pd.date_range("2024-01-01", periods=4, freq="D"),
            "Symbol": ["TEST"] * 4,
            "Close": [100.0, 110.0, 120.0, 130.0],
        }
    )
    signals = pd.DataFrame(
        {
            "Date": data["Date"],
            "Symbol": ["TEST"] * 4,
            "Signal": [1, 1, 1, 0],
        }
    )

    engine = BacktestEngine(initial_capital=1000.0)
    engine.run(data, signals, trust_assessment=trusted_backtest_assessment())

    assert engine.portfolio.positions["TEST"] == 1.0
    assert len(engine.trade_log.trades) == 1
    assert engine.trade_log.trades[0].side == "buy"


def test_backtest_next_bar_execution_is_symbol_specific():
    dates = pd.date_range("2024-01-01", periods=2, freq="D")

    data = pd.DataFrame(
        {
            "Date": [dates[0], dates[0], dates[1], dates[1]],
            "Symbol": ["AAA", "BBB", "AAA", "BBB"],
            "Close": [100.0, 200.0, 110.0, 220.0],
        }
    )

    signals = pd.DataFrame(
        {
            "Date": [dates[0], dates[0], dates[1], dates[1]],
            "Symbol": ["AAA", "BBB", "AAA", "BBB"],
            "Signal": [1, 0, 0, 0],
        }
    )

    engine = BacktestEngine(initial_capital=1000.0)
    engine.run(data, signals, trust_assessment=trusted_backtest_assessment())

    assert len(engine.trade_log.trades) == 1
    assert engine.trade_log.trades[0].symbol == "AAA"
    assert engine.trade_log.trades[0].price == 110.0
    assert engine.trade_log.trades[0].timestamp == dates[1]

def test_backtest_sell_exits_existing_position():
    data = pd.DataFrame(
        {
            "Date": pd.date_range("2024-01-01", periods=3, freq="D"),
            "Symbol": ["TEST"] * 3,
            "Close": [100.0, 110.0, 120.0],
        }
    )
    signals = pd.DataFrame(
        {
            "Date": data["Date"],
            "Symbol": ["TEST"] * 3,
            "Signal": [1, -1, 0],
        }
    )

    engine = BacktestEngine(initial_capital=1000.0)
    engine.run(data, signals, trust_assessment=trusted_backtest_assessment())

    assert engine.portfolio.positions["TEST"] == 0.0
    assert len(engine.trade_log.trades) == 2
    assert engine.trade_log.trades[0].side == "buy"
    assert engine.trade_log.trades[1].side == "sell"


def test_backtest_sell_when_flat_does_not_create_trade():
    data = pd.DataFrame(
        {
            "Date": pd.date_range("2024-01-01", periods=2, freq="D"),
            "Symbol": ["TEST"] * 2,
            "Close": [100.0, 110.0],
        }
    )
    signals = pd.DataFrame(
        {
            "Date": data["Date"],
            "Symbol": ["TEST"] * 2,
            "Signal": [-1, 0],
        }
    )

    engine = BacktestEngine(initial_capital=1000.0)
    engine.run(data, signals, trust_assessment=trusted_backtest_assessment())

    assert engine.portfolio.positions.get("TEST", 0.0) == 0.0
    assert len(engine.trade_log.trades) == 0

def test_backtest_engine_accepts_conditionally_trusted_data():
    data, signals = make_sample_data()

    assessment = assess_data_trust(
        capability="backtest",
        validation_passed=True,
        source_quality=DataTrustState.CONDITIONALLY_TRUSTED,
    )

    engine = BacktestEngine(initial_capital=1000.0)

    metrics = engine.run(
        data,
        signals,
        trust_assessment=assessment,
    )

    assert metrics["total_return"] > 0.0


def test_backtest_engine_rejects_questionable_data_before_execution():
    data, signals = make_sample_data()

    assessment = assess_data_trust(
        capability="backtest",
        validation_passed=True,
        source_quality=DataTrustState.QUESTIONABLE,
    )

    engine = BacktestEngine(initial_capital=1000.0)

    with pytest.raises(ValueError, match="Data Trust requirement failed"):
        engine.run(
            data,
            signals,
            trust_assessment=assessment,
        )

    assert len(engine.trade_log.trades) == 0
    assert engine.portfolio.cash == 1000.0
    assert engine.portfolio.positions == {}
    assert engine.equity_curve is None


def test_backtest_engine_rejects_unresolved_data_before_execution():
    data, signals = make_sample_data()

    assessment = assess_data_trust(
        capability="backtest",
        validation_passed=True,
        source_quality=DataTrustState.UNRESOLVED,
    )

    engine = BacktestEngine(initial_capital=1000.0)

    with pytest.raises(ValueError, match="Data Trust requirement failed"):
        engine.run(
            data,
            signals,
            trust_assessment=assessment,
        )

    assert len(engine.trade_log.trades) == 0
    assert engine.portfolio.cash == 1000.0
    assert engine.portfolio.positions == {}
    assert engine.equity_curve is None



def test_backtest_engine_rejects_invalid_market_data_before_execution():
    data, signals = make_sample_data()
    data.loc[1, "Close"] = -10.0

    engine = BacktestEngine(initial_capital=1000.0)

    with pytest.raises(ValueError, match="positive values"):
        engine.run(data, signals, trust_assessment=trusted_backtest_assessment())

    assert len(engine.trade_log.trades) == 0


def test_portfolio_values_all_open_positions():
    portfolio = Portfolio(initial_capital=500.0)
    portfolio.positions["AAA"] = 1.0
    portfolio.positions["BBB"] = 2.0

    prices = pd.Series(
        [100.0, 200.0],
        index=["AAA", "BBB"],
    )

    assert portfolio.update_value(prices) == 1000.0


def test_backtest_values_all_symbols_at_each_timestamp():
    dates = pd.date_range("2024-01-01", periods=2, freq="D")

    data = pd.DataFrame(
        {
            "Date": [dates[0], dates[0], dates[1], dates[1]],
            "Symbol": ["AAA", "BBB", "AAA", "BBB"],
            "Close": [100.0, 200.0, 110.0, 220.0],
        }
    )

    signals = pd.DataFrame(
        {
            "Date": [dates[0], dates[0], dates[1], dates[1]],
            "Symbol": ["AAA", "BBB", "AAA", "BBB"],
            "Signal": [1, 1, 0, 0],
        }
    )

    engine = BacktestEngine(initial_capital=1000.0)
    result = engine.run(
        data,
        signals,
        trust_assessment=trusted_backtest_assessment(),
    )

    assert engine.portfolio.positions["AAA"] == 1.0
    assert engine.portfolio.positions["BBB"] == 1.0

    # Signals from the first bar execute on the second bar.
    assert engine.portfolio.cash == 670.0

    # Final value includes both open positions at the current prices.
    assert result.equity_curve.iloc[-1] == 1000.0


def test_backtest_multi_symbol_valuation_is_row_order_independent():
    dates = pd.date_range("2024-01-01", periods=2, freq="D")

    data = pd.DataFrame(
        {
            "Date": [dates[0], dates[0], dates[1], dates[1]],
            "Symbol": ["AAA", "BBB", "AAA", "BBB"],
            "Close": [100.0, 200.0, 110.0, 220.0],
        }
    )

    signals = pd.DataFrame(
        {
            "Date": [dates[0], dates[0], dates[1], dates[1]],
            "Symbol": ["AAA", "BBB", "AAA", "BBB"],
            "Signal": [1, 1, 0, 0],
        }
    )

    engine_a = BacktestEngine(initial_capital=1000.0)
    result_a = engine_a.run(
        data,
        signals,
        trust_assessment=trusted_backtest_assessment(),
    )

    reversed_data = data.iloc[[1, 0, 3, 2]].reset_index(drop=True)
    reversed_signals = signals.iloc[[1, 0, 3, 2]].reset_index(drop=True)

    engine_b = BacktestEngine(initial_capital=1000.0)
    result_b = engine_b.run(
        reversed_data,
        reversed_signals,
        trust_assessment=trusted_backtest_assessment(),
    )

    assert result_a.equity_curve.tolist() == result_b.equity_curve.tolist()
    assert engine_a.portfolio.cash == engine_b.portfolio.cash
    assert engine_a.portfolio.positions == engine_b.portfolio.positions
