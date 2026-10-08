def validate_trade_risk(risk, position_sizing=None):
    if not isinstance(risk, dict):
        return {
            "status": "REJECTED",
            "reason": "Invalid risk data",
        }

    if risk.get("status") != "VALID":
        return {
            "status": "REJECTED",
            "reason": "Invalid risk",
        }

    required_risk_fields = (
        "signal",
        "entry",
        "stop_loss",
        "take_profit",
        "risk",
        "reward",
        "risk_reward",
    )

    for field in required_risk_fields:
        if field not in risk:
            return {
                "status": "REJECTED",
                "reason": f"Missing risk field: {field}",
            }

    if risk["risk"] <= 0:
        return {
            "status": "REJECTED",
            "reason": "Invalid risk amount",
        }

    if risk["reward"] <= 0:
        return {
            "status": "REJECTED",
            "reason": "Invalid reward amount",
        }

    if risk["risk_reward"] <= 0:
        return {
            "status": "REJECTED",
            "reason": "Invalid risk reward",
        }

    if position_sizing is not None:
        if not isinstance(position_sizing, dict):
            return {
                "status": "REJECTED",
                "reason": "Invalid position sizing data",
            }

        if position_sizing.get("status") != "VALID":
            return {
                "status": "REJECTED",
                "reason": "Invalid position sizing",
            }

        if position_sizing.get("position_size", 0) <= 0:
            return {
                "status": "REJECTED",
                "reason": "Invalid position size",
            }

    return {
        "status": "APPROVED",
        "signal": risk["signal"],
        "entry": risk["entry"],
        "stop_loss": risk["stop_loss"],
        "take_profit": risk["take_profit"],
        "risk": risk["risk"],
        "reward": risk["reward"],
        "risk_reward": risk["risk_reward"],
    }
