def calculate_risk(signal, entry, stop_loss, take_profit):
    if signal not in ("LONG", "SHORT"):
        return {
            "status": "REJECTED",
            "reason": "Invalid signal",
        }

    if signal == "LONG":
        if stop_loss >= entry:
            return {
                "status": "REJECTED",
                "reason": "Invalid LONG stop loss",
            }

        if take_profit <= entry:
            return {
                "status": "REJECTED",
                "reason": "Invalid LONG take profit",
            }

    elif signal == "SHORT":
        if stop_loss <= entry:
            return {
                "status": "REJECTED",
                "reason": "Invalid SHORT stop loss",
            }

        if take_profit >= entry:
            return {
                "status": "REJECTED",
                "reason": "Invalid SHORT take profit",
            }

    risk = abs(entry - stop_loss)
    reward = abs(take_profit - entry)

    if risk <= 0:
        return {
            "status": "REJECTED",
            "reason": "Zero risk",
        }

    risk_reward = reward / risk

    return {
        "status": "VALID",
        "signal": signal,
        "entry": entry,
        "stop_loss": stop_loss,
        "take_profit": take_profit,
        "risk": risk,
        "reward": reward,
        "risk_reward": risk_reward,
    }


def calculate_smc_risk(signal, entry, structure_level, risk_reward=2):
    if signal not in ("LONG", "SHORT"):
        return {
            "status": "REJECTED",
            "reason": "Invalid signal",
        }

    if risk_reward < 2:
        return {
            "status": "REJECTED",
            "reason": "Risk reward below minimum 1:2",
        }

    if signal == "LONG":
        if structure_level >= entry:
            return {
                "status": "REJECTED",
                "reason": "Invalid LONG structure level",
            }

        stop_loss = structure_level
        risk = entry - stop_loss
        take_profit = entry + (risk * risk_reward)

    else:
        if structure_level <= entry:
            return {
                "status": "REJECTED",
                "reason": "Invalid SHORT structure level",
            }

        stop_loss = structure_level
        risk = stop_loss - entry
        take_profit = entry - (risk * risk_reward)

    reward = abs(take_profit - entry)

    return {
        "status": "VALID",
        "signal": signal,
        "entry": entry,
        "stop_loss": stop_loss,
        "take_profit": take_profit,
        "risk": risk,
        "reward": reward,
        "risk_reward": reward / risk,
    }
