def detect_swings(candles, lookback=2):
    swings = []

    for i in range(lookback, len(candles) - lookback):
        current = candles[i]

        left = candles[i - lookback:i]
        right = candles[i + 1:i + lookback + 1]

        is_swing_high = (
            all(current["high"] > candle["high"] for candle in left)
            and all(current["high"] >= candle["high"] for candle in right)
        )

        is_swing_low = (
            all(current["low"] < candle["low"] for candle in left)
            and all(current["low"] <= candle["low"] for candle in right)
        )

        if is_swing_high:
            swings.append({
                "type": "HIGH",
                "index": i,
                "datetime": current["datetime"],
                "price": current["high"],
            })

        if is_swing_low:
            swings.append({
                "type": "LOW",
                "index": i,
                "datetime": current["datetime"],
                "price": current["low"],
            })

    return swings


def classify_structure(swings):
    highs = [s for s in swings if s["type"] == "HIGH"]
    lows = [s for s in swings if s["type"] == "LOW"]

    for i in range(1, len(highs)):
        highs[i]["structure"] = (
            "HH" if highs[i]["price"] > highs[i - 1]["price"] else "LH"
        )

    for i in range(1, len(lows)):
        lows[i]["structure"] = (
            "HL" if lows[i]["price"] > lows[i - 1]["price"] else "LL"
        )

    return {
        "highs": highs,
        "lows": lows,
    }
