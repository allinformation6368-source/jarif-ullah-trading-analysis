from datetime import datetime, timedelta, timezone


SESSION_PROFILES = {
    "24x7": {
        "weekend_closed": False,
    },
    "weekday": {
        "weekend_closed": True,
    },
}


def _parse_datetime(value):
    try:
        timestamp = datetime.fromisoformat(
            str(value).replace("Z", "+00:00")
        )
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)
        return timestamp.astimezone(timezone.utc)
    except (TypeError, ValueError):
        return None


def _is_weekend_gap(previous, current):
    return (
        previous.weekday() == 4
        and current.weekday() == 0
    ) or (
        previous.weekday() >= 5
        and current.weekday() < 5
    ) or (
        previous.weekday() >= 5
        and current.weekday() >= 5
    )


def validate_session_aware_continuity(
    candles,
    timeframe,
    profile="24x7",
    tolerance=1,
):
    if not isinstance(candles, list) or not candles:
        return {
            "status": "REJECTED",
            "reason": "Empty candle data",
        }

    if profile not in SESSION_PROFILES:
        return {
            "status": "REJECTED",
            "reason": f"Unsupported session profile: {profile}",
        }

    if not isinstance(tolerance, int) or tolerance < 0:
        return {
            "status": "REJECTED",
            "reason": "Invalid continuity tolerance",
        }

    from data.candle_continuity import TIMEFRAME_INTERVALS

    if timeframe not in TIMEFRAME_INTERVALS:
        return {
            "status": "REJECTED",
            "reason": f"Unsupported timeframe: {timeframe}",
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
    allowed_gap = expected * (tolerance + 1)

    for previous, current in zip(timestamps, timestamps[1:]):
        delta = current - previous

        if delta <= timedelta(0):
            return {
                "status": "REJECTED",
                "reason": f"Invalid candle sequence for timeframe {timeframe}",
            }

        if (
            SESSION_PROFILES[profile]["weekend_closed"]
            and _is_weekend_gap(previous, current)
        ):
            continue

        if delta > allowed_gap:
            return {
                "status": "REJECTED",
                "reason": f"Candle gap detected for timeframe {timeframe}",
            }

    return {
        "status": "VALID",
        "candles": len(candles),
        "profile": profile,
    }
