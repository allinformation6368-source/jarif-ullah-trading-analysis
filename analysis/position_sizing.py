def calculate_position_size(
    account_balance,
    risk_percent,
    entry,
    stop_loss,
):
    if account_balance <= 0:
        return {
            "status": "REJECTED",
            "reason": "Invalid account balance",
        }

    if risk_percent <= 0:
        return {
            "status": "REJECTED",
            "reason": "Invalid risk percent",
        }

    if entry <= 0 or stop_loss <= 0:
        return {
            "status": "REJECTED",
            "reason": "Invalid price",
        }

    risk_amount = account_balance * (risk_percent / 100)
    price_risk = abs(entry - stop_loss)

    if price_risk <= 0:
        return {
            "status": "REJECTED",
            "reason": "Entry and stop loss are equal",
        }

    position_size = risk_amount / price_risk

    return {
        "status": "VALID",
        "account_balance": account_balance,
        "risk_percent": risk_percent,
        "risk_amount": risk_amount,
        "entry": entry,
        "stop_loss": stop_loss,
        "price_risk": price_risk,
        "position_size": position_size,
    }
