from datetime import datetime, timedelta, timezone

from data.candle_freshness import (
    TIMEFRAME_MAX_AGE,
    validate_candle_freshness,
    validate_latest_candle_freshness,
)


NOW = datetime(
    2026,
    10,
    8,
    12,
    0,
    tzinfo=timezone.utc,
)


def candle_at(timestamp):
    return {
        "datetime": timestamp.isoformat(),
        "open": 100.0,
        "high": 110.0,
        "low": 95.0,
        "close": 105.0,
        "volume": None,
    }


def test_fresh_candle_is_valid():
    candle = candle_at(
        NOW - timedelta(minutes=2)
    )

    result = validate_candle_freshness(
        candle,
        "1min",
        now=NOW,
    )

    assert result["status"] == "VALID"


def test_stale_candle_is_rejected():
    candle = candle_at(
        NOW - timedelta(minutes=6)
    )

    result = validate_candle_freshness(
        candle,
        "1min",
        now=NOW,
    )

    assert result["status"] == "REJECTED"
    assert result["reason"] == "Stale candle for timeframe 1min"


def test_future_candle_is_rejected():
    candle = candle_at(
        NOW + timedelta(minutes=1)
    )

    result = validate_candle_freshness(
        candle,
        "1min",
        now=NOW,
    )

    assert result["status"] == "REJECTED"
    assert result["reason"] == "Future candle for timeframe 1min"


def test_invalid_datetime_is_rejected():
    candle = candle_at(NOW)
    candle["datetime"] = "bad"

    result = validate_candle_freshness(
        candle,
        "1min",
        now=NOW,
    )

    assert result["status"] == "REJECTED"
    assert result["reason"] == "Invalid candle datetime"


def test_unsupported_timeframe_is_rejected():
    candle = candle_at(NOW)

    result = validate_candle_freshness(
        candle,
        "2min",
        now=NOW,
    )

    assert result["status"] == "REJECTED"
    assert result["reason"] == "Unsupported timeframe: 2min"


def test_naive_datetime_is_treated_as_utc():
    candle = candle_at(NOW)
    candle["datetime"] = "2026-10-08T12:00:00"

    result = validate_candle_freshness(
        candle,
        "1min",
        now=NOW,
    )

    assert result["status"] == "VALID"


def test_latest_candle_freshness_uses_last_candle():
    candles = [
        candle_at(NOW - timedelta(minutes=10)),
        candle_at(NOW - timedelta(minutes=2)),
    ]

    result = validate_latest_candle_freshness(
        candles,
        "1min",
        now=NOW,
    )

    assert result["status"] == "VALID"


def test_latest_candle_freshness_rejects_empty():
    result = validate_latest_candle_freshness(
        [],
        "1min",
        now=NOW,
    )

    assert result["status"] == "REJECTED"
    assert "Empty candle data" in result["reason"]


def test_all_expected_timeframes_have_thresholds():
    assert set(TIMEFRAME_MAX_AGE) == {
        "1min",
        "5min",
        "15min",
        "1h",
        "4h",
        "1day",
        "1week",
    }
