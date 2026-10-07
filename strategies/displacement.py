def detect_displacement(candles, multiplier=1.5):
    if len(candles) < 2:
        return []

    bodies = [
        abs(c["close"] - c["open"])
        for c in candles
    ]

    average_body = sum(bodies) / len(bodies)

    if average_body == 0:
        return []

    displacement = []

    for i, candle in enumerate(candles):
        body = abs(candle["close"] - candle["open"])

        if body >= average_body * multiplier:
            direction = (
                "BULLISH"
                if candle["close"] > candle["open"]
                else "BEARISH"
            )

            displacement.append({
                "type": direction,
                "index": i,
                "datetime": candle["datetime"],
                "open": candle["open"],
                "close": candle["close"],
                "body": body,
                "strength": body / average_body,
            })

    return displacement
