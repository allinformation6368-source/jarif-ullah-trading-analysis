def validate_runtime_config(
    api_key=None,
    account_balance=10000,
    risk_percent=1.0,
):
    if not isinstance(api_key, str) or not api_key.strip():
        return {
            "status": "REJECTED",
            "reason": "Missing API key",
        }

    if not isinstance(account_balance, (int, float)):
        return {
            "status": "REJECTED",
            "reason": "Invalid account balance",
        }

    if account_balance <= 0:
        return {
            "status": "REJECTED",
            "reason": "Invalid account balance",
        }

    if not isinstance(risk_percent, (int, float)):
        return {
            "status": "REJECTED",
            "reason": "Invalid risk percent",
        }

    if risk_percent <= 0:
        return {
            "status": "REJECTED",
            "reason": "Invalid risk percent",
        }

    if risk_percent > 100:
        return {
            "status": "REJECTED",
            "reason": "Risk percent exceeds 100",
        }

    return {
        "status": "VALID",
        "account_balance": float(account_balance),
        "risk_percent": float(risk_percent),
        "api_key_configured": True,
    }
