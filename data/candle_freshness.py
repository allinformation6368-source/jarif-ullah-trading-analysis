from datetime import datetime, timedelta, timezone


TIMEFRAME_MAX_AGE = {
    "1min": timedelta(minutes=5),
    "5min": timedelta(minutes=15),
    "15min": timedelta(minutes=45),
    "1h": timedelta(hours=3),
    "4h": timedelta(hours=12),
    "1day": timedelta(days=3),
    "1week": timedelta(days=14),
}


def _parse_datetime(value):
    try:
        return datetime.fromisoformat(
            str(value).replace("Z", "+00:00")
        )
    except (TypeError, ValueError):
        return None


def validate_candle_freshness(
    candle,
    timeframe,
    now=None,
):
    if not isinstance(candle, dict):
        return {
            "status": "REJECTED",
            "reason": "Invalid candle",
        }

    if timeframe not in TIMEFRAME_MAX_AGE:
        return {
            "status": "REJECTED",
            "reason": f"Unsupported timeframe: {timeframe}",
        }

    timestamp = _parse_datetime(candle.get("datetime"))

    if timestamp is None:
        return {
            "status": "REJECTED",
            "reason": "Invalid candle datetime",
        }

    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)

    timestamp = timestamp.astimezone(timezone.utc)

    if now is None:
        now = datetime.now(timezone.utc)
    elif now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    else:
        now = now.astimezone(timezone.utc)

    if timestamp > now:
        return {
            "status": "REJECTED",
            "reason": f"Future candle for timeframe {timeframe}",
        }

    age = now - timestamp

    if age > TIMEFRAME_MAX_AGE[timeframe]:
        return {
            "status": "REJECTED",
            "reason": f"Stale candle for timeframe {timeframe}",
        }

    return {
        "status": "VALID",
        "age_seconds": age.total_seconds(),
    }


def validate_latest_candle_freshness(
    candles,
    timeframe,
    now=None,
):
    if not isinstance(candles, list) or not candles:
        return {
            "status": "REJECTED",
            "reason": f"Empty candle data for timeframe {timeframe}",
        }

    return validate_candle_freshness(
        candle=candles[-1],
        timeframe=timeframe,
        now=now,
    )
