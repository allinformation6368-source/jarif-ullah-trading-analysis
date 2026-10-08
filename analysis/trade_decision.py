MIN_ENTRY_CONFIDENCE = 60


def evaluate_trade_decision(confluence):
    signal = confluence["signal"]
    confidence = confluence["confidence"]

    if (
        signal in ("LONG", "SHORT")
        and confidence >= MIN_ENTRY_CONFIDENCE
    ):
        decision = "ENTRY_READY"
    else:
        decision = "WAIT"

    return {
        "decision": decision,
        "signal": signal,
        "confidence": confidence,
    }
