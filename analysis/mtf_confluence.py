def calculate_mtf_confluence(results):
    score = 0
    reasons = []

    for timeframe, analysis in results.items():
        confluence = analysis["confluence"]

        score += confluence["score"]

        signal = confluence["signal"]

        if signal == "LONG":
            reasons.append(f"{timeframe}: LONG")
        elif signal == "SHORT":
            reasons.append(f"{timeframe}: SHORT")
        else:
            reasons.append(f"{timeframe}: WAIT")

    if score >= 4:
        signal = "LONG"
    elif score <= -4:
        signal = "SHORT"
    else:
        signal = "WAIT"

    confidence = min(abs(score) * 10, 100)

    return {
        "signal": signal,
        "score": score,
        "confidence": confidence,
        "reasons": reasons,
    }
