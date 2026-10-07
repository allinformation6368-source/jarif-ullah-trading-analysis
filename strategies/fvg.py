def detect_fvg(candles):
    fvgs = []

    for i in range(2, len(candles)):
        first = candles[i - 2]
        middle = candles[i - 1]
        third = candles[i]

        if third["low"] > first["high"]:
            fvgs.append({
                "type": "BULLISH_FVG",
                "index": i,
                "datetime": third["datetime"],
                "low": first["high"],
                "high": third["low"],
                "size": third["low"] - first["high"],
            })

        elif third["high"] < first["low"]:
            fvgs.append({
                "type": "BEARISH_FVG",
                "index": i,
                "datetime": third["datetime"],
                "low": third["high"],
                "high": first["low"],
                "size": first["low"] - third["high"],
            })

    return fvgs
