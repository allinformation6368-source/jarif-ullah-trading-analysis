from strategies.price_action import detect_swings, classify_structure


def analyze_structure(candles, lookback=2):
    swings = detect_swings(candles, lookback=lookback)
    structure = classify_structure(swings)

    highs = structure["highs"]
    lows = structure["lows"]

    labels = []

    for item in highs:
        if "structure" in item:
            labels.append(item["structure"])

    for item in lows:
        if "structure" in item:
            labels.append(item["structure"])

    recent = labels[-6:]

    bullish_score = recent.count("HH") + recent.count("HL")
    bearish_score = recent.count("LH") + recent.count("LL")

    if bullish_score > bearish_score:
        bias = "BULLISH"
    elif bearish_score > bullish_score:
        bias = "BEARISH"
    else:
        bias = "NEUTRAL"

    return {
        "bias": bias,
        "swings": swings,
        "highs": highs,
        "lows": lows,
        "recent_structure": recent,
    }
