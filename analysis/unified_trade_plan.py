def build_unified_trade_plan(
    decision,
    risk,
    position_sizing=None,
    risk_guard=None,
    entry_quality=None,
):
    if not isinstance(decision, dict):
        return {
            "status": "REJECTED",
            "reason": "Invalid decision data",
        }

    if decision.get("decision") != "ENTRY_READY":
        return {
            "status": "WAIT",
            "reason": "Trade entry is not ready",
        }

    if not isinstance(risk, dict) or risk.get("status") != "VALID":
        return {
            "status": "REJECTED",
            "reason": "Invalid risk",
        }

    if risk_guard is not None:
        if not isinstance(risk_guard, dict):
            return {
                "status": "REJECTED",
                "reason": "Invalid risk guard",
            }

        if risk_guard.get("status") != "APPROVED":
            return {
                "status": "REJECTED",
                "reason": "Risk guard rejected trade",
            }

    if position_sizing is not None:
        if not isinstance(position_sizing, dict):
            return {
                "status": "REJECTED",
                "reason": "Invalid position sizing",
            }

        if position_sizing.get("status") != "VALID":
            return {
                "status": "REJECTED",
                "reason": "Invalid position sizing",
            }

    plan = {
        "status": "READY",
        "signal": decision.get("signal"),
        "entry": risk["entry"],
        "stop_loss": risk["stop_loss"],
        "take_profit": risk["take_profit"],
        "risk": risk["risk"],
        "reward": risk["reward"],
        "risk_reward": risk["risk_reward"],
    }

    if risk.get("sl_source") is not None:
        plan["sl_source"] = risk["sl_source"]

    if position_sizing is not None:
        plan["account_balance"] = position_sizing.get("account_balance")
        plan["risk_percent"] = position_sizing.get("risk_percent")
        plan["risk_amount"] = position_sizing.get("risk_amount")
        plan["position_size"] = position_sizing.get("position_size")

    if risk_guard is not None:
        plan["risk_guard"] = risk_guard["status"]

    if entry_quality is not None:
        plan["entry_quality"] = entry_quality

    return plan
