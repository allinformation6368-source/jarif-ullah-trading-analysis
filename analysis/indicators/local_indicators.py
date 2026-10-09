from math import sqrt


def _values(candles, key="close"):
    values = []
    for candle in candles or []:
        try:
            value = float(candle[key])
        except (KeyError, TypeError, ValueError):
            continue
        values.append(value)
    return values


def sma(candles, period, key="close"):
    values = _values(candles, key)

    if period <= 0:
        raise ValueError("period must be positive")

    if len(values) < period:
        return None

    return sum(values[-period:]) / period


def ema(candles, period, key="close"):
    values = _values(candles, key)

    if period <= 0:
        raise ValueError("period must be positive")

    if len(values) < period:
        return None

    result = sum(values[:period]) / period
    multiplier = 2 / (period + 1)

    for value in values[period:]:
        result = ((value - result) * multiplier) + result

    return result


def rsi(candles, period=14, key="close"):
    values = _values(candles, key)

    if period <= 0:
        raise ValueError("period must be positive")

    if len(values) <= period:
        return None

    gains = []
    losses = []

    for previous, current in zip(values[:-1], values[1:]):
        change = current - previous
        gains.append(max(change, 0.0))
        losses.append(max(-change, 0.0))

    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period

    for gain, loss in zip(gains[period:], losses[period:]):
        avg_gain = ((avg_gain * (period - 1)) + gain) / period
        avg_loss = ((avg_loss * (period - 1)) + loss) / period

    if avg_loss == 0:
        return 100.0

    relative_strength = avg_gain / avg_loss
    return 100 - (100 / (1 + relative_strength))


def true_range(candle, previous_close=None):
    try:
        high = float(candle["high"])
        low = float(candle["low"])
    except (KeyError, TypeError, ValueError):
        return None

    if previous_close is None:
        return high - low

    return max(
        high - low,
        abs(high - previous_close),
        abs(low - previous_close),
    )


def atr(candles, period=14):
    if period <= 0:
        raise ValueError("period must be positive")

    valid = []

    previous_close = None

    for candle in candles or []:
        current_close = None

        try:
            current_close = float(candle["close"])
        except (KeyError, TypeError, ValueError):
            pass

        tr = true_range(candle, previous_close)

        if tr is not None:
            valid.append(tr)

        if current_close is not None:
            previous_close = current_close

    if len(valid) < period:
        return None

    return sum(valid[-period:]) / period


def volatility(candles, period=20, key="close"):
    values = _values(candles, key)

    if period <= 1:
        raise ValueError("period must be greater than 1")

    if len(values) < period:
        return None

    window = values[-period:]
    mean = sum(window) / period

    variance = sum((value - mean) ** 2 for value in window) / period

    return sqrt(variance)


def macd(
    candles,
    fast_period=12,
    slow_period=26,
    signal_period=9,
    key="close",
):
    values = _values(candles, key)

    if fast_period <= 0 or slow_period <= 0 or signal_period <= 0:
        raise ValueError("periods must be positive")

    if fast_period >= slow_period:
        raise ValueError("fast_period must be less than slow_period")

    if len(values) < slow_period + signal_period - 1:
        return None

    def ema_values(data, period):
        if len(data) < period:
            return []

        result = sum(data[:period]) / period
        multiplier = 2 / (period + 1)
        output = [result]

        for value in data[period:]:
            result = ((value - result) * multiplier) + result
            output.append(result)

        return output

    fast = ema_values(values, fast_period)
    slow = ema_values(values, slow_period)

    offset = slow_period - fast_period
    aligned_fast = fast[offset:]

    macd_values = [
        fast_value - slow_value
        for fast_value, slow_value in zip(aligned_fast, slow)
    ]

    if len(macd_values) < signal_period:
        return None

    signal_values = ema_values(macd_values, signal_period)

    if not signal_values:
        return None

    signal = signal_values[-1]
    line = macd_values[-1]

    return {
        "macd": line,
        "signal": signal,
        "histogram": line - signal,
    }


def trend(candles, fast_period=20, slow_period=50, key="close"):
    fast = ema(candles, fast_period, key)
    slow = ema(candles, slow_period, key)

    if fast is None or slow is None:
        return "UNKNOWN"

    if fast > slow:
        return "BULLISH"

    if fast < slow:
        return "BEARISH"

    return "NEUTRAL"


def support_resistance(candles, lookback=20):
    if lookback <= 0:
        raise ValueError("lookback must be positive")

    recent = list(candles or [])[-lookback:]

    highs = []
    lows = []

    for candle in recent:
        try:
            highs.append(float(candle["high"]))
            lows.append(float(candle["low"]))
        except (KeyError, TypeError, ValueError):
            continue

    if not highs or not lows:
        return None

    return {
        "support": min(lows),
        "resistance": max(highs),
    }


def analyze_local(candles):
    return {
        "sma_20": sma(candles, 20),
        "ema_20": ema(candles, 20),
        "ema_50": ema(candles, 50),
        "rsi_14": rsi(candles, 14),
        "macd": macd(candles),
        "atr_14": atr(candles, 14),
        "volatility_20": volatility(candles, 20),
        "trend": trend(candles),
        "support_resistance": support_resistance(candles),
    }
