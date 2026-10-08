MODE_WEIGHTS = {
    "scalping": {
        "1min": 1,
        "5min": 2,
        "15min": 3,
        "1h": 4,
    },
    "intraday": {
        "5min": 1,
        "15min": 2,
        "1h": 3,
        "4h": 4,
    },
    "swing": {
        "4h": 1,
        "1day": 2,
        "1week": 3,
    },
}

DEFAULT_WEIGHTS = {
    "1h": 3,
    "15m": 2,
    "5m": 1,
}


def calculate_mtf_confluence(results, mode=None):
    weights = MODE_WEIGHTS.get(mode, DEFAULT_WEIGHTS)

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
