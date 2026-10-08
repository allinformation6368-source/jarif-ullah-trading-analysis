from datetime import datetime, timezone

from analysis.paper_performance import calculate_account_performance


def create_paper_session(
    symbol=None,
    mode=None,
    starting_balance=10000,
    timestamp=None,
):
    if not isinstance(starting_balance, (int, float)):
        return {
            "status": "REJECTED",
            "reason": "Invalid starting balance",
        }

    if starting_balance <= 0:
        return {
            "status": "REJECTED",
            "reason": "Invalid starting balance",
        }

    if timestamp is None:
        timestamp = datetime.now(timezone.utc).isoformat()

    return {
        "status": "READY",
        "symbol": symbol,
        "mode": mode,
        "timestamp": timestamp,
        "starting_balance": float(starting_balance),
        "orders": [],
    }


def add_session_order(session, order):
    if not isinstance(session, dict):
        return {
            "status": "REJECTED",
            "reason": "Invalid session",
        }

    if session.get("status") != "READY":
        return {
            "status": "REJECTED",
            "reason": "Session is not ready",
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

    session["orders"].append(dict(order))

    return {
        "status": "ADDED",
        "orders": len(session["orders"]),
    }


def get_session_performance(session):
    if not isinstance(session, dict):
        return {
            "status": "REJECTED",
            "reason": "Invalid session",
        }

    if session.get("status") != "READY":
        return {
            "status": "REJECTED",
            "reason": "Session is not ready",
        }

    orders = session.get("orders")

    if not isinstance(orders, list):
        return {
            "status": "REJECTED",
            "reason": "Invalid session orders",
        }

    account = {
        "status": "READY",
        "starting_balance": session["starting_balance"],
        "orders": orders,
        "realized_pnl": sum(
            order.get("pnl", 0)
            for order in orders
            if isinstance(order, dict)
            and order.get("status") == "CLOSED"
        ),
    }

    performance = calculate_account_performance(account)

    if performance["status"] != "VALID":
        return performance

    return {
        "status": "VALID",
        "symbol": session.get("symbol"),
        "mode": session.get("mode"),
        "timestamp": session.get("timestamp"),
        "performance": performance,
    }


def close_paper_session(session):
    performance = get_session_performance(session)

    if performance["status"] != "VALID":
        return performance

    session["status"] = "CLOSED"

    return {
        "status": "CLOSED",
        "symbol": session.get("symbol"),
        "mode": session.get("mode"),
        "timestamp": session.get("timestamp"),
        "performance": performance["performance"],
    }
