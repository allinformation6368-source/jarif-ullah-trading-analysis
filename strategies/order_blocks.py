def detect_order_blocks(candles, body_multiplier=1.5):
    order_blocks = []
    if len(candles) < 3:
        return order_blocks
    bodies = [abs(candle["close"] - candle["open"]) for candle in candles]
    average_body = sum(bodies) / len(bodies)
    if average_body == 0:
        return order_blocks
    for i in range(1, len(candles)):
        previous = candles[i - 1]
        current = candles[i]
        current_body = abs(current["close"] - current["open"])
        displacement = current_body >= average_body * body_multiplier
        if not displacement:
            continue
        if previous["close"] < previous["open"] and current["close"] > current["open"]:
            order_blocks.append({"type": "BULLISH_OB", "index": i - 1, "datetime": previous["datetime"], "high": previous["high"], "low": previous["low"], "displacement_index": i})
        elif previous["close"] > previous["open"] and current["close"] < current["open"]:
            order_blocks.append({"type": "BEARISH_OB", "index": i - 1, "datetime": previous["datetime"], "high": previous["high"], "low": previous["low"], "displacement_index": i})
    return order_blocks
