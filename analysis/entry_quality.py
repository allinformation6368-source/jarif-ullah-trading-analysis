def evaluate_entry_quality(confluence, decision):
    signal = confluence["signal"]
    decision_status = decision["decision"]

    if signal not in ("LONG", "SHORT"):
        return {
            "status": "REJECTED",
            "reason": "No directional signal",
        }

    if decision_status != "ENTRY_READY":
        return {
            "status": "REJECTED",
            "reason": "Trade decision is not entry ready",
        }

    if decision["signal"] != signal:
        return {
            "status": "REJECTED",
            "reason": "Signal mismatch",
        }

    return {
        "status": "VALID",
        "signal": signal,
    }
