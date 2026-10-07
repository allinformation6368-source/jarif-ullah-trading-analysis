def detect_liquidity_sweeps(candles, liquidity, tolerance=0.001):
    sweeps = []
    pools = liquidity["buy_side_liquidity"] + liquidity["sell_side_liquidity"]
    candle_map = {candle["datetime"]: i for i, candle in enumerate(candles)}
    for pool in pools:
        pool_time = max(pool["datetime_a"], pool["datetime_b"])
        start_index = candle_map.get(pool_time)
        if start_index is None:
            continue
        start_index += 1
        if pool["type"] == "BSL":
            level = max(pool["price_a"], pool["price_b"])
            for i in range(start_index, len(candles)):
                candle = candles[i]
                if candle["high"] > level:
                    sweeps.append({"type": "BSL_SWEEP", "index": i, "datetime": candle["datetime"], "level": level, "high": candle["high"], "close": candle["close"], "rejection": candle["close"] < level})
                    break
        elif pool["type"] == "SSL":
            level = min(pool["price_a"], pool["price_b"])
            for i in range(start_index, len(candles)):
                candle = candles[i]
                if candle["low"] < level:
                    sweeps.append({"type": "SSL_SWEEP", "index": i, "datetime": candle["datetime"], "level": level, "low": candle["low"], "close": candle["close"], "rejection": candle["close"] > level})
                    break
    return sweeps
