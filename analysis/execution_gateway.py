from analysis.execution_audit import (
    create_execution_audit,
    persist_execution_audit,
)

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
        "risk_guard",
    )

    for field in required_fields:
        if field not in order:
            return {
                "status": "REJECTED",
                "reason": f"Missing order field: {field}",
            }

    if order["risk_guard"] != "APPROVED":
        return {
            "status": "REJECTED",
            "reason": "Risk guard approval required",
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

    paper_order = {
        "status": "OPEN",
        "signal": order["signal"],
        "entry": order["entry"],
        "stop_loss": order["stop_loss"],
        "take_profit": order["take_profit"],
        "risk_guard": order["risk_guard"],
        "account_balance": account_balance,
        "exit_price": None,
        "result": None,
        "pnl": 0,
    }

    return {
        "status": "PAPER_ACCEPTED",
        "mode": "PAPER",
        "signal": order["signal"],
        "entry": order["entry"],
        "stop_loss": order["stop_loss"],
        "take_profit": order["take_profit"],
        "risk_guard": order["risk_guard"],
        "account_balance": account_balance,
        "risk_percent": risk_percent,
        "risk_reward": risk_reward,
        "order": paper_order,
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
            result = execute_live_order(order)
        else:
            result = execution_config

        result["audit"] = create_execution_audit(
            result=result,
            order=order,
            mode=mode,
        )
        persist_execution_audit(result["audit"])

        return result

    result = execute_paper_order(
        order=order,
        account_balance=account_balance,
        risk_percent=risk_percent,
        risk_reward=risk_reward,
    )

    result["audit"] = create_execution_audit(
        result=result,
        order=order,
        mode=mode,
    )
    persist_execution_audit(result["audit"])

    return result
