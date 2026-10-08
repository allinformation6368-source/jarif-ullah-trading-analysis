def create_paper_order(
    trade_plan,
    account_balance=10000,
):
    if not isinstance(trade_plan, dict):
        return {
            "status": "REJECTED",
            "reason": "Invalid trade plan",
        }

    if trade_plan.get("status") != "READY":
        return {
            "status": "REJECTED",
            "reason": "Trade plan is not ready",
        }

    required_fields = (
        "signal",
        "entry",
        "stop_loss",
        "take_profit",
    )

    for field in required_fields:
        if field not in trade_plan:
            return {
                "status": "REJECTED",
                "reason": f"Missing trade field: {field}",
            }

    if account_balance <= 0:
        return {
            "status": "REJECTED",
            "reason": "Invalid account balance",
        }

    signal = trade_plan["signal"]

    if signal not in ("BUY", "SELL"):
        return {
            "status": "REJECTED",
            "reason": "Invalid signal",
        }

    return {
        "status": "OPEN",
        "signal": signal,
        "entry": trade_plan["entry"],
        "stop_loss": trade_plan["stop_loss"],
        "take_profit": trade_plan["take_profit"],
        "account_balance": account_balance,
        "exit_price": None,
        "result": None,
        "pnl": 0,
    }


def update_paper_order(order, candle):
    if not isinstance(order, dict):
        return {
            "status": "REJECTED",
            "reason": "Invalid order",
        }

    if order.get("status") != "OPEN":
        return {
            "status": "REJECTED",
            "reason": "Order is not open",
        }

    if not isinstance(candle, dict):
        return {
            "status": "REJECTED",
            "reason": "Invalid candle",
        }

    high = candle.get("high")
    low = candle.get("low")

    if high is None or low is None:
        return {
            "status": "REJECTED",
            "reason": "Missing candle price",
        }

    signal = order["signal"]
    entry = order["entry"]
    stop_loss = order["stop_loss"]
    take_profit = order["take_profit"]

    if signal == "BUY":
        if low <= stop_loss:
            order.update({
                "status": "CLOSED",
                "result": "LOSS",
                "exit_price": stop_loss,
                "pnl": stop_loss - entry,
            })
        elif high >= take_profit:
            order.update({
                "status": "CLOSED",
                "result": "WIN",
                "exit_price": take_profit,
                "pnl": take_profit - entry,
            })

    elif signal == "SELL":
        if high >= stop_loss:
            order.update({
                "status": "CLOSED",
                "result": "LOSS",
                "exit_price": stop_loss,
                "pnl": entry - stop_loss,
            })
        elif low <= take_profit:
            order.update({
                "status": "CLOSED",
                "result": "WIN",
                "exit_price": take_profit,
                "pnl": entry - take_profit,
            })

    return order


def calculate_paper_balance(
    starting_balance,
    orders,
):
    if starting_balance <= 0:
        return {
            "status": "REJECTED",
            "reason": "Invalid starting balance",
        }

    if not isinstance(orders, list):
        return {
            "status": "REJECTED",
            "reason": "Invalid orders",
        }

    closed_orders = [
        order
        for order in orders
        if order.get("status") == "CLOSED"
    ]

    total_pnl = sum(
        order.get("pnl", 0)
        for order in closed_orders
    )

    return {
        "status": "VALID",
        "starting_balance": starting_balance,
        "total_pnl": total_pnl,
        "ending_balance": starting_balance + total_pnl,
        "closed_trades": len(closed_orders),
    }
