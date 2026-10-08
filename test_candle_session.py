from data.candle_session import (
    validate_session_aware_continuity,
)


def candle(timestamp):
    return {
        "datetime": timestamp,
        "open": 100.0,
        "high": 110.0,
        "low": 95.0,
        "close": 105.0,
    }


def test_24x7_continuity_rejects_large_weekend_gap():
    result = validate_session_aware_continuity(
        [
            candle("2026-01-02 23:00:00"),
            candle("2026-01-03 23:00:00"),
        ],
        "1h",
        profile="24x7",
    )

    assert result["status"] == "REJECTED"


def test_weekday_profile_allows_weekend_gap():
    result = validate_session_aware_continuity(
        [
            candle("2026-01-02 23:00:00"),
            candle("2026-01-05 00:00:00"),
        ],
        "1h",
        profile="weekday",
    )

    assert result["status"] == "VALID"


def test_weekday_profile_rejects_large_weekday_gap():
    result = validate_session_aware_continuity(
        [
            candle("2026-01-05 10:00:00"),
            candle("2026-01-05 20:00:00"),
        ],
        "1h",
        profile="weekday",
    )

    assert result["status"] == "REJECTED"


def test_24x7_normal_continuity_is_valid():
    result = validate_session_aware_continuity(
        [
            candle("2026-01-01 00:00:00"),
            candle("2026-01-01 01:00:00"),
            candle("2026-01-01 02:00:00"),
        ],
        "1h",
        profile="24x7",
    )

    assert result["status"] == "VALID"


def test_invalid_profile_is_rejected():
    result = validate_session_aware_continuity(
        [candle("2026-01-01 00:00:00")],
        "1h",
        profile="unknown",
    )

    assert result["status"] == "REJECTED"


def test_invalid_datetime_is_rejected():
    result = validate_session_aware_continuity(
        [candle("invalid")],
        "1h",
    )

    assert result["status"] == "REJECTED"


def test_invalid_timeframe_is_rejected():
    result = validate_session_aware_continuity(
        [candle("2026-01-01 00:00:00")],
        "2min",
    )

    assert result["status"] == "REJECTED"


def test_empty_candles_are_rejected():
    result = validate_session_aware_continuity(
        [],
        "1h",
    )

    assert result["status"] == "REJECTED"


def test_session_continuity_accepts_naive_and_utc_timestamps():
    result = validate_session_aware_continuity(
        [
            candle("2026-01-01 00:00:00"),
            candle("2026-01-01T01:00:00+00:00"),
        ],
        "1h",
    )

    assert result["status"] == "VALID"


def test_session_continuity_normalizes_timezone_offsets():
    result = validate_session_aware_continuity(
        [
            candle("2026-01-01T00:00:00+00:00"),
            candle("2026-01-01T06:30:00+05:30"),
        ],
        "1h",
    )

    assert result["status"] == "VALID"
