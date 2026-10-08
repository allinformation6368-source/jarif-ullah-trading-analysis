DEFAULT_ACCOUNT_BALANCE = 10000
DEFAULT_RISK_PERCENT = 1.0

MIN_RISK_PERCENT = 0.01
MAX_RISK_PERCENT = 5.0

DEFAULT_RISK_REWARD = 2.0

DEFAULT_EXECUTION_MODE = "PAPER"
ALLOWED_EXECUTION_MODES = ("PAPER", "LIVE")


def validate_risk_config(
    account_balance=DEFAULT_ACCOUNT_BALANCE,
    risk_percent=DEFAULT_RISK_PERCENT,
    risk_reward=DEFAULT_RISK_REWARD,
):
    if account_balance <= 0:
        return {
            "status": "REJECTED",
            "reason": "Invalid account balance",
        }

    if not (
        MIN_RISK_PERCENT
        <= risk_percent
        <= MAX_RISK_PERCENT
    ):
        return {
            "status": "REJECTED",
            "reason": "Risk percent outside allowed range",
        }

    if risk_reward <= 0:
        return {
            "status": "REJECTED",
            "reason": "Invalid risk reward",
        }

    return {
        "status": "VALID",
        "account_balance": account_balance,
        "risk_percent": risk_percent,
        "risk_reward": risk_reward,
    }


def validate_execution_mode(mode=DEFAULT_EXECUTION_MODE):
    if mode not in ALLOWED_EXECUTION_MODES:
        return {
            "status": "REJECTED",
            "reason": "Invalid execution mode",
        }

    if mode == "LIVE":
        return {
            "status": "REJECTED",
            "mode": "LIVE",
            "reason": "Live execution requires explicit broker adapter",
        }

    return {
        "status": "VALID",
        "mode": mode,
    }
