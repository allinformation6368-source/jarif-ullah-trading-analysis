def _calculate_trade_result(
    signal,
    entry,
    stop_loss,
    take_profit,
    candles,
):
    for candle in candles:
        high = candle["high"]
        low = candle["low"]

        if signal == "BUY":
            if low <= stop_loss:
                return {
                    "result": "LOSS",
                    "exit_price": stop_loss,
                    "pnl": stop_loss - entry,
                }

            if high >= take_profit:
                return {
                    "result": "WIN",
                    "exit_price": take_profit,
                    "pnl": take_profit - entry,
                }

        elif signal == "SELL":
            if high >= stop_loss:
                return {
                    "result": "LOSS",
                    "exit_price": stop_loss,
                    "pnl": entry - stop_loss,
                }

            if low <= take_profit:
                return {
                    "result": "WIN",
                    "exit_price": take_profit,
                    "pnl": entry - take_profit,
                }

    return {
        "result": "OPEN",
        "exit_price": None,
        "pnl": 0,
    }


def calculate_backtest_statistics(trades):
    closed = [
        trade
        for trade in trades
        if trade.get("result") in ("WIN", "LOSS")
    ]

    wins = [
        trade
        for trade in closed
        if trade["result"] == "WIN"
    ]

    losses = [
        trade
        for trade in closed
        if trade["result"] == "LOSS"
    ]

    total_pnl = sum(
        trade.get("pnl", 0)
        for trade in closed
    )

    win_rate = (
        len(wins) / len(closed) * 100
        if closed
        else 0
    )

    return {
        "status": "VALID",
        "total_trades": len(trades),
        "closed_trades": len(closed),
        "wins": len(wins),
        "losses": len(losses),
        "win_rate": win_rate,
        "total_pnl": total_pnl,
    }


def run_backtest(
    candles,
    analyze_function,
    account_balance=10000,
    risk_percent=1,
    lookback=20,
):
    if not candles:
        return {
            "status": "WAIT",
            "trades": [],
            "statistics": calculate_backtest_statistics([]),
        }

    if len(candles) <= lookback:
        return {
            "status": "WAIT",
            "trades": [],
            "statistics": calculate_backtest_statistics([]),
        }

    trades = []

    for index in range(lookback, len(candles)):
        history = candles[:index + 1]

        result = analyze_function(
            history,
            account_balance=account_balance,
            risk_percent=risk_percent,
        )

        trade_plan = result.get("trade_plan")

        if not isinstance(trade_plan, dict):
            continue

        if trade_plan.get("status") != "READY":
            continue

        signal = trade_plan.get("signal")
        entry = trade_plan.get("entry")
        stop_loss = trade_plan.get("stop_loss")
        take_profit = trade_plan.get("take_profit")

        if None in (
            signal,
            entry,
            stop_loss,
            take_profit,
        ):
            continue

        future_candles = candles[index + 1:]

        outcome = _calculate_trade_result(
            signal=signal,
            entry=entry,
            stop_loss=stop_loss,
            take_profit=take_profit,
            candles=future_candles,
        )

        trades.append({
            "index": index,
            "signal": signal,
            "entry": entry,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "result": outcome["result"],
            "exit_price": outcome["exit_price"],
            "pnl": outcome["pnl"],
        })

    return {
        "status": "VALID",
        "trades": trades,
        "statistics": calculate_backtest_statistics(trades),
    }
