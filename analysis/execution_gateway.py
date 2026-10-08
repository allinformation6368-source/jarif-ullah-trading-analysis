from config.risk import (
    DEFAULT_EXECUTION_MODE,
    DEFAULT_ACCOUNT_BALANCE,
    DEFAULT_RISK_PERCENT,
    DEFAULT_RISK_REWARD,
    validate_execution_mode,
    validate_risk_config,
)


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


def execute_paper_order(
    order,
    account_balance=DEFAULT_ACCOUNT_BALANCE,
    risk_percent=DEFAULT_RISK_PERCENT,
    risk_reward=DEFAULT_RISK_REWARD,
):
    validation = validate_execution_order(order)

    if validation["status"] != "VALID":
        return validation

    risk_config = validate_risk_config(
        account_balance=account_balance,
        risk_percent=risk_percent,
        risk_reward=risk_reward,
    )

    if risk_config["status"] != "VALID":
        return risk_config

    return {
        "status": "PAPER_ACCEPTED",
        "mode": "PAPER",
        "signal": order["signal"],
        "entry": order["entry"],
        "stop_loss": order["stop_loss"],
        "take_profit": order["take_profit"],
        "account_balance": account_balance,
        "risk_percent": risk_percent,
        "risk_reward": risk_reward,
    }


def execute_live_order(order):
    return {
        "status": "REJECTED",
        "mode": "LIVE",
        "reason": "Live execution adapter is not enabled",
    }


def execute_order(
    order,
    mode=DEFAULT_EXECUTION_MODE,
    account_balance=DEFAULT_ACCOUNT_BALANCE,
    risk_percent=DEFAULT_RISK_PERCENT,
    risk_reward=DEFAULT_RISK_REWARD,
):
    execution_config = validate_execution_mode(mode)

    if execution_config["status"] != "VALID":
        if mode == "LIVE":
            return execute_live_order(order)
        return execution_config

    return execute_paper_order(
        order=order,
        account_balance=account_balance,
        risk_percent=risk_percent,
        risk_reward=risk_reward,
    )
