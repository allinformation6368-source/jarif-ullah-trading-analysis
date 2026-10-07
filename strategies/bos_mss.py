def detect_bos_mss(candles, swings, sweeps):
    signals = []

    highs = [s for s in swings if s["type"] == "HIGH"]
    lows = [s for s in swings if s["type"] == "LOW"]

    for sweep in sweeps:
        index = sweep["index"]

        previous_highs = [
            h for h in highs
            if h["index"] < index
        ]

        previous_lows = [
            l for l in lows
            if l["index"] < index
        ]

        if sweep["type"] == "SSL_SWEEP" and previous_highs:
            target = previous_highs[-1]

            for i in range(index + 1, len(candles)):
                if candles[i]["close"] > target["price"]:
                    signals.append({
                        "type": "BULLISH_MSS",
                        "sweep_index": index,
                        "break_index": i,
                        "break_price": target["price"],
                        "datetime": candles[i]["datetime"],
                    })
                    break

        elif sweep["type"] == "BSL_SWEEP" and previous_lows:
            target = previous_lows[-1]

            for i in range(index + 1, len(candles)):
                if candles[i]["close"] < target["price"]:
                    signals.append({
                        "type": "BEARISH_MSS",
                        "sweep_index": index,
                        "break_index": i,
                        "break_price": target["price"],
                        "datetime": candles[i]["datetime"],
                    })
                    break

    return signals
