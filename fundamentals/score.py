def calculate_fundamental_score(risk_result):
    score = 0

    high = risk_result.get("high_events", 0)
    medium = risk_result.get("medium_events", 0)
    low = risk_result.get("low_events", 0)

    score += high * 35
    score += medium * 20
    score += low * 8

    score = min(score, 100)

    if score >= 80:
        level = "EXTREME"
    elif score >= 60:
        level = "HIGH"
    elif score >= 30:
        level = "MODERATE"
    elif score > 0:
        level = "LOW"
    else:
        level = "NONE"

    return {
        "score": score,
        "level": level,
    }
