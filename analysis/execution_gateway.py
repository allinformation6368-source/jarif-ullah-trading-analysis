def validate_execution_order(order):
    if not isinstance(order, dict):
        return {
            "status": "REJECTED",
            "reason": "Invalid order",
        }

    required_fields = (
        "signal",
        "entry",
        "stop_loss",
        "take_profit",
    )

    for field in required_fields:
        if field not in order:
            return {
                "status": "REJECTED",
                "reason": f"Missing order field: {field}",
            }

    if order["signal"] not in ("BUY", "SELL"):
        return {
            "status": "REJECTED",
            "reason": "Invalid signal",
        }

    return {
        "status": "VALID",
    }


def execute_paper_order(order):
    validation = validate_execution_order(order)

    if validation["status"] != "VALID":
        return validation

    return {
        "status": "PAPER_ACCEPTED",
        "mode": "PAPER",
        "signal": order["signal"],
        "entry": order["entry"],
        "stop_loss": order["stop_loss"],
        "take_profit": order["take_profit"],
    }


def execute_live_order(order):
    return {
        "status": "REJECTED",
        "mode": "LIVE",
        "reason": "Live execution adapter is not enabled",
    }


def execute_order(order, mode="PAPER"):
    if mode == "PAPER":
        return execute_paper_order(order)

    if mode == "LIVE":
        return execute_live_order(order)

    return {
        "status": "REJECTED",
        "reason": "Invalid execution mode",
    }
