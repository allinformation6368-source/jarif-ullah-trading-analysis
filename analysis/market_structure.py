def _ohlc(candles):
    result = []

    for candle in candles or []:
        try:
            result.append(
                {
                    "high": float(candle["high"]),
                    "low": float(candle["low"]),
                    "close": float(candle["close"]),
                    "datetime": candle.get("datetime")
                    or candle.get("timestamp")
                    or candle.get("time"),
                }
            )
        except (KeyError, TypeError, ValueError):
            continue

    return result


def swing_points(candles, left=2, right=2):
    if left <= 0 or right <= 0:
        raise ValueError("left and right must be positive")

    data = _ohlc(candles)
    highs = []
    lows = []

    for i in range(left, len(data) - right):
        current = data[i]

        left_highs = [x["high"] for x in data[i - left:i]]
        right_highs = [x["high"] for x in data[i + 1:i + right + 1]]

        left_lows = [x["low"] for x in data[i - left:i]]
        right_lows = [x["low"] for x in data[i + 1:i + right + 1]]

        if current["high"] > max(left_highs + right_highs):
            highs.append(
                {
                    "index": i,
                    "price": current["high"],
                    "datetime": current["datetime"],
                }
            )

        if current["low"] < min(left_lows + right_lows):
            lows.append(
                {
                    "index": i,
                    "price": current["low"],
                    "datetime": current["datetime"],
                }
            )

    return {
        "swing_highs": highs,
        "swing_lows": lows,
    }


def structure_bias(candles, left=2, right=2):
    points = swing_points(candles, left, right)

    highs = points["swing_highs"]
    lows = points["swing_lows"]

    if len(highs) < 2 or len(lows) < 2:
        return "UNKNOWN"

    higher_high = highs[-1]["price"] > highs[-2]["price"]
    higher_low = lows[-1]["price"] > lows[-2]["price"]

    lower_high = highs[-1]["price"] < highs[-2]["price"]
    lower_low = lows[-1]["price"] < lows[-2]["price"]

    if higher_high and higher_low:
        return "BULLISH"

    if lower_high and lower_low:
        return "BEARISH"

    return "RANGE"


def liquidity_levels(candles, left=2, right=2):
    points = swing_points(candles, left, right)

    highs = points["swing_highs"]
    lows = points["swing_lows"]

    return {
        "buy_side_liquidity": (
            highs[-1]["price"] if highs else None
        ),
        "sell_side_liquidity": (
            lows[-1]["price"] if lows else None
        ),
        "swing_highs": highs,
        "swing_lows": lows,
    }


def liquidity_sweep(candles, left=2, right=2):
    data = _ohlc(candles)

    if not data:
        return {
            "sweep": False,
            "direction": None,
            "level": None,
        }

    # The latest candle cannot itself be a confirmed swing because
    # confirmation requires candles to its right. For sweep detection,
    # use only the candles before the latest candle to establish the
    # previously confirmed liquidity level.
    levels = liquidity_levels(data[:-1], left, right)

    latest = data[-1]

    buy_side = levels["buy_side_liquidity"]
    sell_side = levels["sell_side_liquidity"]

    # Bearish liquidity sweep:
    # price trades above buy-side liquidity but closes back below it.
    if (
        buy_side is not None
        and latest["high"] > buy_side
        and latest["close"] < buy_side
    ):
        return {
            "sweep": True,
            "direction": "BEARISH",
            "level": buy_side,
        }

    # Bullish liquidity sweep:
    # price trades below sell-side liquidity but closes back above it.
    if (
        sell_side is not None
        and latest["low"] < sell_side
        and latest["close"] > sell_side
    ):
        return {
            "sweep": True,
            "direction": "BULLISH",
            "level": sell_side,
        }

    return {
        "sweep": False,
        "direction": None,
        "level": None,
    }


def market_structure_shift(candles, left=2, right=2):
    data = _ohlc(candles)

    if len(data) < 3:
        return {
            "mss": False,
            "direction": None,
            "broken_level": None,
        }

    points = swing_points(data, left, right)

    highs = points["swing_highs"]
    lows = points["swing_lows"]

    latest_close = data[-1]["close"]

    # Bullish MSS: latest close breaks the most recent swing high.
    if highs and latest_close > highs[-1]["price"]:
        return {
            "mss": True,
            "direction": "BULLISH",
            "broken_level": highs[-1]["price"],
        }

    # Bearish MSS: latest close breaks the most recent swing low.
    if lows and latest_close < lows[-1]["price"]:
        return {
            "mss": True,
            "direction": "BEARISH",
            "broken_level": lows[-1]["price"],
        }

    return {
        "mss": False,
        "direction": None,
        "broken_level": None,
    }


def analyze_market_structure(candles):
    points = swing_points(candles)

    return {
        "structure": structure_bias(candles),
        "swing_points": points,
        "liquidity": liquidity_levels(candles),
        "sweep": liquidity_sweep(candles),
        "mss": market_structure_shift(candles),
    }
