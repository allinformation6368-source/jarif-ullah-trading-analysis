def detect_market_regime(candles):
    if not candles or len(candles) < 4:
        return {
            "status": "WAIT",
            "regime": "NEUTRAL",
            "reason": "Insufficient candles",
        }

    closes = [c["close"] for c in candles]
    highs = [c["high"] for c in candles]
    lows = [c["low"] for c in candles]

    recent_closes = closes[-4:]
    recent_highs = highs[-4:]
    recent_lows = lows[-4:]

    bullish_structure = (
        recent_closes[-1] > recent_closes[0]
        and recent_highs[-1] > recent_highs[0]
        and recent_lows[-1] > recent_lows[0]
    )

    bearish_structure = (
        recent_closes[-1] < recent_closes[0]
        and recent_highs[-1] < recent_highs[0]
        and recent_lows[-1] < recent_lows[0]
    )

    price_range = max(recent_highs) - min(recent_lows)
    close_range = max(recent_closes) - min(recent_closes)

    if price_range <= 0:
        return {
            "status": "VALID",
            "regime": "NEUTRAL",
            "reason": "No meaningful price range",
        }

    range_ratio = close_range / price_range

    if bullish_structure and range_ratio >= 0.45:
        regime = "TRENDING_BULLISH"
    elif bearish_structure and range_ratio >= 0.45:
        regime = "TRENDING_BEARISH"
    elif range_ratio < 0.30:
        regime = "RANGING"
    else:
        regime = "NEUTRAL"

    return {
        "status": "VALID",
        "regime": regime,
        "range_ratio": range_ratio,
        "sample_size": len(recent_closes),
    }
