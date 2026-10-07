def detect_liquidity_pools(swings, tolerance=0.001):
    highs = [s for s in swings if s["type"] == "HIGH"]
    lows = [s for s in swings if s["type"] == "LOW"]

    buy_side = []
    sell_side = []

    for i in range(len(highs)):
        for j in range(i + 1, len(highs)):
            a = highs[i]["price"]
            b = highs[j]["price"]

            if abs(a - b) / max(a, b) <= tolerance:
                buy_side.append({
                    "type": "BSL",
                    "price_a": a,
                    "price_b": b,
                    "datetime_a": highs[i]["datetime"],
                    "datetime_b": highs[j]["datetime"],
                })

    for i in range(len(lows)):
        for j in range(i + 1, len(lows)):
            a = lows[i]["price"]
            b = lows[j]["price"]

            if abs(a - b) / max(a, b) <= tolerance:
                sell_side.append({
                    "type": "SSL",
                    "price_a": a,
                    "price_b": b,
                    "datetime_a": lows[i]["datetime"],
                    "datetime_b": lows[j]["datetime"],
                })

    return {
        "buy_side_liquidity": buy_side,
        "sell_side_liquidity": sell_side,
    }
