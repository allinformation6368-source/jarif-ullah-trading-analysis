from datetime import datetime, timedelta


TIMEFRAME_INTERVALS = {
    "1min": timedelta(minutes=1),
    "5min": timedelta(minutes=5),
    "15min": timedelta(minutes=15),
    "1h": timedelta(hours=1),
    "4h": timedelta(hours=4),
    "1day": timedelta(days=1),
    "1week": timedelta(weeks=1),
}


def _parse_datetime(value):
    try:
        return datetime.fromisoformat(
            str(value).replace("Z", "+00:00")
        )
    except (TypeError, ValueError):
        return None


def validate_candle_continuity(candles, timeframe, tolerance=1):
    if not isinstance(candles, list) or not candles:
        return {
            "status": "REJECTED",
            "reason": "Empty candle data",
        }

    if timeframe not in TIMEFRAME_INTERVALS:
        return {
            "status": "REJECTED",
            "reason": f"Unsupported timeframe: {timeframe}",
        }

    if not isinstance(tolerance, int) or tolerance < 0:
        return {
            "status": "REJECTED",
            "reason": "Invalid continuity tolerance",
        }

    timestamps = []

    for candle in candles:
        if not isinstance(candle, dict):
            return {
                "status": "REJECTED",
                "reason": "Invalid candle",
            }

        timestamp = _parse_datetime(candle.get("datetime"))

        if timestamp is None:
            return {
                "status": "REJECTED",
                "reason": "Invalid candle datetime",
            }

        timestamps.append(timestamp)

    expected = TIMEFRAME_INTERVALS[timeframe]

    for previous, current in zip(timestamps, timestamps[1:]):
        delta = current - previous

        if delta <= timedelta(0):
            return {
                "status": "REJECTED",
                "reason": f"Invalid candle sequence for timeframe {timeframe}",
            }

        allowed_gap = expected * (tolerance + 1)

        if delta > allowed_gap:
            return {
                "status": "REJECTED",
                "reason": f"Candle gap detected for timeframe {timeframe}",
            }

    return {
        "status": "VALID",
        "candles": len(candles),
    }
