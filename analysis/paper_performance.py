def _validate_trades(trades):
    if not isinstance(trades, (list, tuple)):
        return {
            "status": "REJECTED",
            "reason": "Trades must be a list or tuple",
        }

    for trade in trades:
        if not isinstance(trade, dict):
            return {
                "status": "REJECTED",
                "reason": "Each trade must be a dictionary",
            }

        if "pnl" not in trade:
            return {
                "status": "REJECTED",
                "reason": "Trade is missing pnl",
            }

        if not isinstance(trade["pnl"], (int, float)):
            return {
                "status": "REJECTED",
                "reason": "Trade pnl must be numeric",
            }

    return {"status": "VALID"}


def calculate_max_drawdown(pnls, starting_equity=0.0):
    if not isinstance(starting_equity, (int, float)):
        return 0.0

    equity = float(starting_equity)
    peak = equity
    max_drawdown = 0.0

    for pnl in pnls:
        equity += float(pnl)
        peak = max(peak, equity)
        drawdown = peak - equity
        max_drawdown = max(max_drawdown, drawdown)

    return max_drawdown


def calculate_paper_performance(trades, starting_equity=0.0):
    validation = _validate_trades(trades)

    if validation["status"] != "VALID":
        return validation

    if not isinstance(starting_equity, (int, float)):
        return {
            "status": "REJECTED",
            "reason": "Starting equity must be numeric",
        }

    pnls = [float(trade["pnl"]) for trade in trades]

    wins = [pnl for pnl in pnls if pnl > 0]
    losses = [pnl for pnl in pnls if pnl < 0]

    total = len(pnls)
    winning_trades = len(wins)
    losing_trades = len(losses)

    gross_profit = sum(wins)
    gross_loss = abs(sum(losses))
    net_pnl = sum(pnls)

    if total:
        win_rate = (winning_trades / total) * 100
        average_pnl = net_pnl / total
    else:
        win_rate = 0.0
        average_pnl = 0.0

    if gross_loss > 0:
        profit_factor = gross_profit / gross_loss
    elif gross_profit > 0:
        profit_factor = float("inf")
    else:
        profit_factor = 0.0

    max_drawdown = calculate_max_drawdown(
        pnls,
        starting_equity=starting_equity,
    )

    ending_equity = float(starting_equity) + net_pnl

    r_values = []
    for trade in trades:
        risk_amount = trade.get("risk_amount")
        if isinstance(risk_amount, (int, float)) and risk_amount > 0:
            r_values.append(float(trade["pnl"]) / float(risk_amount))

    average_r = (
        sum(r_values) / len(r_values)
        if r_values
        else 0.0
    )

    return {
        "status": "VALID",
        "total_trades": total,
        "winning_trades": winning_trades,
        "losing_trades": losing_trades,
        "win_rate": win_rate,
        "gross_profit": gross_profit,
        "gross_loss": gross_loss,
        "net_pnl": net_pnl,
        "average_pnl": average_pnl,
        "profit_factor": profit_factor,
        "max_drawdown": max_drawdown,
        "starting_equity": float(starting_equity),
        "ending_equity": ending_equity,
        "average_r": average_r,
    }


def calculate_account_performance(account):
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

    orders = account.get("orders")

    if not isinstance(orders, list):
        return {
            "status": "REJECTED",
            "reason": "Invalid account orders",
        }

    closed_trades = [
        order
        for order in orders
        if isinstance(order, dict)
        and order.get("status") == "CLOSED"
    ]

    starting_equity = account.get("starting_balance", 0.0)

    result = calculate_paper_performance(
        closed_trades,
        starting_equity=starting_equity,
    )

    if result["status"] != "VALID":
        return result

    result["open_trades"] = sum(
        1
        for order in orders
        if isinstance(order, dict)
        and order.get("status") == "OPEN"
    )

    result["account_realized_pnl"] = account.get(
        "realized_pnl",
        result["net_pnl"],
    )

    return result


def calculate_orders_performance(orders, starting_balance=0.0):
    if not isinstance(orders, list):
        return {
            "status": "REJECTED",
            "reason": "Invalid orders",
        }

    closed_orders = [
        order
        for order in orders
        if isinstance(order, dict)
        and order.get("status") == "CLOSED"
    ]

    return calculate_paper_performance(
        closed_orders,
        starting_equity=starting_balance,
    )
