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

    if trade_plan.get("risk_guard") != "APPROVED":
        return {
            "status": "REJECTED",
            "reason": "Risk guard approval required",
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
        "risk_guard": trade_plan["risk_guard"],
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


def process_paper_position(order, candles):
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

    if not isinstance(candles, list):
        return {
            "status": "REJECTED",
            "reason": "Invalid candles",
        }

    for candle in candles:
        result = update_paper_order(
            order=order,
            candle=candle,
        )

        if result.get("status") == "CLOSED":
            return result

        if result.get("status") == "REJECTED":
            return result

    return order


def calculate_open_positions(orders):
    if not isinstance(orders, list):
        return {
            "status": "REJECTED",
            "reason": "Invalid orders",
        }

    open_orders = [
        order
        for order in orders
        if isinstance(order, dict)
        and order.get("status") == "OPEN"
    ]

    return {
        "status": "VALID",
        "open_positions": len(open_orders),
        "orders": open_orders,
    }


def create_paper_account(starting_balance=10000):
    if starting_balance <= 0:
        return {
            "status": "REJECTED",
            "reason": "Invalid starting balance",
        }

    return {
        "status": "READY",
        "starting_balance": starting_balance,
        "balance": starting_balance,
        "realized_pnl": 0,
        "equity": starting_balance,
        "orders": [],
    }


def add_paper_order(account, order):
    if not isinstance(account, dict):
        return {
            "status": "REJECTED",
            "reason": "Invalid account",
        }

    if account.get("status") != "READY":
        return {
            "status": "REJECTED",
            "reason": "Account is not ready",
        }

    if not isinstance(order, dict):
        return {
            "status": "REJECTED",
            "reason": "Invalid order",
        }

    if order.get("status") not in ("OPEN", "CLOSED"):
        return {
            "status": "REJECTED",
            "reason": "Invalid order status",
        }

    account["orders"].append(dict(order))

    if order.get("status") == "CLOSED":
        account["realized_pnl"] += order.get("pnl", 0)

    account["balance"] = (
        account["starting_balance"]
        + account["realized_pnl"]
    )

    account["equity"] = account["balance"]

    return {
        "status": "ADDED",
        "balance": account["balance"],
        "realized_pnl": account["realized_pnl"],
        "equity": account["equity"],
        "orders": len(account["orders"]),
    }


def update_paper_account(account, orders):
    if not isinstance(account, dict):
        return {
            "status": "REJECTED",
            "reason": "Invalid account",
        }

    if account.get("status") != "READY":
        return {
            "status": "REJECTED",
            "reason": "Account is not ready",
        }

    if not isinstance(orders, list):
        return {
            "status": "REJECTED",
            "reason": "Invalid orders",
        }

    realized_pnl = sum(
        order.get("pnl", 0)
        for order in orders
        if isinstance(order, dict)
        and order.get("status") == "CLOSED"
    )

    account["orders"] = [
        dict(order)
        for order in orders
    ]

    account["realized_pnl"] = realized_pnl
    account["balance"] = (
        account["starting_balance"]
        + realized_pnl
    )
    account["equity"] = account["balance"]

    return {
        "status": "UPDATED",
        "starting_balance": account["starting_balance"],
        "balance": account["balance"],
        "realized_pnl": account["realized_pnl"],
        "equity": account["equity"],
        "orders": len(account["orders"]),
    }


def run_paper_session(
    candles,
    analyze_function,
    account_balance=10000,
    risk_percent=1,
):
    if not isinstance(candles, list):
        return {
            "status": "REJECTED",
            "reason": "Invalid candles",
        }

    if not candles:
        return {
            "status": "WAIT",
            "orders": [],
            "account": create_paper_account(account_balance),
        }

    account = create_paper_account(account_balance)

    if account.get("status") != "READY":
        return account

    orders = []

    for index in range(len(candles)):
        history = candles[:index + 1]

        result = analyze_function(
            history,
            account_balance=account["balance"],
            risk_percent=risk_percent,
        )

        if not isinstance(result, dict):
            continue

        trade_plan = result.get("trade_plan")

        if not isinstance(trade_plan, dict):
            continue

        if trade_plan.get("status") != "READY":
            continue

        order = create_paper_order(
            trade_plan=trade_plan,
            account_balance=account["balance"],
        )

        if order.get("status") != "OPEN":
            continue

        future_candles = candles[index + 1:]

        if future_candles:
            order = process_paper_position(
                order=order,
                candles=future_candles,
            )

        orders.append(order)

        update_paper_account(
            account=account,
            orders=orders,
        )

    return {
        "status": "VALID",
        "orders": orders,
        "account": account,
    }
