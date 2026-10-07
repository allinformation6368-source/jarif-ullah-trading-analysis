def calculate_mtf_confluence(results):
    weights = {
        "1h": 3,
        "15m": 2,
        "5m": 1,
    }

    score = 0
    reasons = []

    max_weighted_score = 0

    for timeframe, analysis in results.items():
        confluence = analysis["confluence"]
        raw_score = confluence["score"]

        weight = weights.get(timeframe, 1)
        weighted_score = raw_score * weight

        score += weighted_score
        max_weighted_score += 10 * weight

        signal = confluence["signal"]

        reasons.append(
            f"{timeframe}: {signal} "
            f"(score={raw_score}, weight={weight})"
        )

    if score >= 4:
        signal = "LONG"
    elif score <= -4:
        signal = "SHORT"
    else:
        signal = "WAIT"

    if max_weighted_score > 0:
        confidence = round(
            abs(score) / max_weighted_score * 100
        )
    else:
        confidence = 0

    return {
        "signal": signal,
        "score": score,
        "confidence": confidence,
        "reasons": reasons,
    }
