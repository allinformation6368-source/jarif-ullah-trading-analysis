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


def calculate_smc_risk_from_analysis(
    signal,
    entry,
    analysis,
    risk_reward=2,
):
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

    structure = analysis.get("structure", {})
    order_blocks = analysis.get("order_blocks", [])

    if signal == "LONG":
        lows = structure.get("lows", [])

        valid_lows = [
            low for low in lows
            if low.get("price") < entry
        ]

        if valid_lows:
            structure_level = valid_lows[-1]["price"]
            sl_source = "STRUCTURE"
        else:
            bullish_obs = [
                ob for ob in order_blocks
                if (
                    ob.get("type") == "BULLISH_OB"
                    and ob.get("low") < entry
                )
            ]

            if not bullish_obs:
                return {
                    "status": "REJECTED",
                    "reason": "No valid LONG risk anchor",
                }

            structure_level = bullish_obs[-1]["low"]
            sl_source = "ORDER_BLOCK"

    else:
        highs = structure.get("highs", [])

        valid_highs = [
            high for high in highs
            if high.get("price") > entry
        ]

        if valid_highs:
            structure_level = valid_highs[-1]["price"]
            sl_source = "STRUCTURE"
        else:
            bearish_obs = [
                ob for ob in order_blocks
                if (
                    ob.get("type") == "BEARISH_OB"
                    and ob.get("high") > entry
                )
            ]

            if not bearish_obs:
                return {
                    "status": "REJECTED",
                    "reason": "No valid SHORT risk anchor",
                }

            structure_level = bearish_obs[-1]["high"]
            sl_source = "ORDER_BLOCK"

    result = calculate_smc_risk(
        signal=signal,
        entry=entry,
        structure_level=structure_level,
        risk_reward=risk_reward,
    )

    if result["status"] != "VALID":
        return result

    result["sl_source"] = sl_source

    return result
