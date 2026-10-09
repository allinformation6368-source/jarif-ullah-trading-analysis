from datetime import datetime, timezone


def _parse_timestamp(value):
    if isinstance(value, datetime):
        dt = value
    elif isinstance(value, str):
        text = value.strip().replace("Z", "+00:00")

        # TwelveData commonly returns: YYYY-MM-DD HH:MM:SS
        try:
            dt = datetime.fromisoformat(text)
        except ValueError:
            return None
    else:
        return None

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    return dt


def candle_timestamp(candle):
    if not isinstance(candle, dict):
        return None

    for key in ("datetime", "timestamp", "time", "date"):
        if key in candle:
            parsed = _parse_timestamp(candle[key])
            if parsed is not None:
                return parsed

    return None


def latest_candle(candles):
    if not candles:
        return None

    valid = [
        candle for candle in candles
        if candle_timestamp(candle) is not None
    ]

    if not valid:
        return None

    return max(valid, key=lambda candle: candle_timestamp(candle))


def latest_candle_id(candles):
    candle = latest_candle(candles)

    if candle is None:
        return None

    timestamp = candle_timestamp(candle)

    return timestamp.isoformat()


class CandleGuard:
    """
    Tracks the latest processed candle per symbol/timeframe.

    Same candle => duplicate.
    Newer candle => process.
    Older candle => stale/out-of-order.
    """

    def __init__(self):
        self._processed = {}

    def key(self, symbol, timeframe):
        return f"{symbol}|{timeframe}"

    def check(self, symbol, timeframe, candles):
        candle_id = latest_candle_id(candles)

        if candle_id is None:
            return {
                "status": "INVALID",
                "process": False,
                "reason": "No valid candle timestamp",
            }

        key = self.key(symbol, timeframe)
        previous = self._processed.get(key)

        if previous is None:
            return {
                "status": "NEW",
                "process": True,
                "candle_id": candle_id,
            }

        if candle_id == previous:
            return {
                "status": "DUPLICATE",
                "process": False,
                "candle_id": candle_id,
                "previous_candle_id": previous,
            }

        if candle_id < previous:
            return {
                "status": "STALE",
                "process": False,
                "candle_id": candle_id,
                "previous_candle_id": previous,
            }

        return {
            "status": "NEW",
            "process": True,
            "candle_id": candle_id,
            "previous_candle_id": previous,
        }

    def mark_processed(self, symbol, timeframe, candles):
        candle_id = latest_candle_id(candles)

        if candle_id is None:
            return False

        key = self.key(symbol, timeframe)
        self._processed[key] = candle_id
        return True

    def snapshot(self):
        return dict(self._processed)

    def clear(self):
        self._processed.clear()
