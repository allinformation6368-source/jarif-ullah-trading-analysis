from datetime import datetime, timezone


def create_execution_audit(
    result,
    order=None,
    mode=None,
):
    if not isinstance(result, dict):
        return {
            "status": "REJECTED",
            "reason": "Invalid execution result",
        }

    if order is not None and not isinstance(order, dict):
        return {
            "status": "REJECTED",
            "reason": "Invalid order",
        }

    timestamp = datetime.now(timezone.utc).isoformat()

    return {
        "timestamp": timestamp,
        "execution_status": result.get("status"),
        "mode": result.get("mode", mode),
        "signal": (
            order.get("signal")
            if isinstance(order, dict)
            else result.get("signal")
        ),
        "entry": (
            order.get("entry")
            if isinstance(order, dict)
            else result.get("entry")
        ),
        "stop_loss": (
            order.get("stop_loss")
            if isinstance(order, dict)
            else result.get("stop_loss")
        ),
        "take_profit": (
            order.get("take_profit")
            if isinstance(order, dict)
            else result.get("take_profit")
        ),
        "account_balance": result.get("account_balance"),
        "risk_percent": result.get("risk_percent"),
        "risk_reward": result.get("risk_reward"),
        "reason": result.get("reason"),
    }


def is_execution_successful(audit):
    if not isinstance(audit, dict):
        return False

    return audit.get("execution_status") in (
        "PAPER_ACCEPTED",
    )
