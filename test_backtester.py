from analysis.backtester import (
    _calculate_trade_result,
    calculate_backtest_statistics,
    run_backtest,
)


def test_buy_trade_win():
    candles = [
        {"high": 106, "low": 100},
    ]

    result = _calculate_trade_result(
        signal="BUY",
        entry=100,
        stop_loss=95,
        take_profit=105,
        candles=candles,
    )

    assert result["result"] == "WIN"
    assert result["exit_price"] == 105
    assert result["pnl"] == 5


def test_buy_trade_loss():
    candles = [
        {"high": 103, "low": 94},
    ]

    result = _calculate_trade_result(
        signal="BUY",
        entry=100,
        stop_loss=95,
        take_profit=105,
        candles=candles,
    )

    assert result["result"] == "LOSS"
    assert result["exit_price"] == 95
    assert result["pnl"] == -5


def test_sell_trade_win():
    candles = [
        {"high": 101, "low": 94},
    ]

    result = _calculate_trade_result(
        signal="SELL",
        entry=100,
        stop_loss=105,
        take_profit=95,
        candles=candles,
    )

    assert result["result"] == "WIN"
    assert result["exit_price"] == 95
    assert result["pnl"] == 5


def test_sell_trade_loss():
    candles = [
        {"high": 106, "low": 98},
    ]

    result = _calculate_trade_result(
        signal="SELL",
        entry=100,
        stop_loss=105,
        take_profit=95,
        candles=candles,
    )

    assert result["result"] == "LOSS"
    assert result["exit_price"] == 105
    assert result["pnl"] == -5


def test_open_trade():
    candles = [
        {"high": 103, "low": 98},
    ]

    result = _calculate_trade_result(
        signal="BUY",
        entry=100,
        stop_loss=95,
        take_profit=105,
        candles=candles,
    )

    assert result["result"] == "OPEN"
    assert result["exit_price"] is None
    assert result["pnl"] == 0


def test_statistics():
    trades = [
        {"result": "WIN", "pnl": 10},
        {"result": "LOSS", "pnl": -5},
        {"result": "WIN", "pnl": 8},
    ]

    result = calculate_backtest_statistics(trades)

    assert result["status"] == "VALID"
    assert result["total_trades"] == 3
    assert result["closed_trades"] == 3
    assert result["wins"] == 2
    assert result["losses"] == 1
    assert result["win_rate"] == (2 / 3) * 100
    assert result["total_pnl"] == 13


def test_empty_backtest():
    result = run_backtest(
        candles=[],
        analyze_function=lambda *args, **kwargs: {},
    )

    assert result["status"] == "WAIT"
    assert result["trades"] == []
    assert result["statistics"]["total_trades"] == 0


def test_short_data_waits():
    candles = [
        {"high": 101, "low": 99}
        for _ in range(5)
    ]

    result = run_backtest(
        candles=candles,
        analyze_function=lambda *args, **kwargs: {},
        lookback=20,
    )

    assert result["status"] == "WAIT"
    assert result["trades"] == []


def test_backtest_uses_analysis_function():
    calls = []

    def fake_analyzer(
        history,
        account_balance=None,
        risk_percent=None,
    ):
        calls.append(len(history))

        return {
            "trade_plan": {
                "status": "READY",
                "signal": "BUY",
                "entry": 100,
                "stop_loss": 95,
                "take_profit": 105,
            }
        }

    candles = [
        {"high": 106, "low": 99}
        for _ in range(8)
    ]

    result = run_backtest(
        candles=candles,
        analyze_function=fake_analyzer,
        lookback=5,
    )

    assert result["status"] == "VALID"
    assert len(calls) == 3
    assert result["statistics"]["total_trades"] == 3


def test_backtest_with_real_mtf_engine():
    from analysis.mtf_engine import analyze_multi_timeframe

    candles = []

    for i in range(25):
        candles.append({
            "datetime": f"2026-10-07T10:{i:02d}:00+00:00",
            "open": 100 + i,
            "high": 103 + i,
            "low": 98 + i,
            "close": 102 + i,
        })

    def analyze_mtf(history, account_balance=10000, risk_percent=1):
        return analyze_multi_timeframe(
            {
                "5m": history,
                "15m": history,
                "1h": history,
            },
            account_balance=account_balance,
            risk_percent=risk_percent,
        )

    result = run_backtest(
        candles=candles,
        analyze_function=analyze_mtf,
        account_balance=10000,
        risk_percent=1,
        lookback=20,
    )

    assert result["status"] == "VALID"
    assert "trades" in result
    assert "statistics" in result
    assert result["statistics"]["total_trades"] >= 0
