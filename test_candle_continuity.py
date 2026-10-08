from data.candle_continuity import (
    validate_candle_continuity,
)


def candle(timestamp):
    return {
        "datetime": timestamp,
        "open": 100.0,
        "high": 110.0,
        "low": 95.0,
        "close": 105.0,
    }


def test_continuous_1min_candles_are_valid():
    result = validate_candle_continuity(
        [
            candle("2026-01-01 00:00:00"),
            candle("2026-01-01 00:01:00"),
            candle("2026-01-01 00:02:00"),
        ],
        "1min",
    )

    assert result["status"] == "VALID"


def test_small_gap_within_tolerance_is_valid():
    result = validate_candle_continuity(
        [
            candle("2026-01-01 00:00:00"),
            candle("2026-01-01 00:02:00"),
        ],
        "1min",
        tolerance=1,
    )

    assert result["status"] == "VALID"


def test_large_gap_is_rejected():
    result = validate_candle_continuity(
        [
            candle("2026-01-01 00:00:00"),
            candle("2026-01-01 00:10:00"),
        ],
        "1min",
    )

    assert result["status"] == "REJECTED"
    assert "gap" in result["reason"].lower()


def test_out_of_order_candles_are_rejected():
    result = validate_candle_continuity(
        [
            candle("2026-01-01 00:02:00"),
            candle("2026-01-01 00:01:00"),
        ],
        "1min",
    )

    assert result["status"] == "REJECTED"


def test_invalid_timeframe_is_rejected():
    result = validate_candle_continuity(
        [
            candle("2026-01-01 00:00:00"),
            candle("2026-01-01 00:01:00"),
        ],
        "2min",
    )

    assert result["status"] == "REJECTED"


def test_invalid_datetime_is_rejected():
    result = validate_candle_continuity(
        [
            candle("not-a-date"),
        ],
        "1min",
    )

    assert result["status"] == "REJECTED"


def test_empty_candles_are_rejected():
    result = validate_candle_continuity([], "1min")

    assert result["status"] == "REJECTED"


def test_invalid_tolerance_is_rejected():
    result = validate_candle_continuity(
        [
            candle("2026-01-01 00:00:00"),
        ],
        "1min",
        tolerance=-1,
    )

    assert result["status"] == "REJECTED"


def test_all_supported_timeframes_have_intervals():
    for timeframe in (
        "1min",
        "5min",
        "15min",
        "1h",
        "4h",
        "1day",
        "1week",
    ):
        result = validate_candle_continuity(
            [candle("2026-01-01 00:00:00")],
            timeframe,
        )

        assert result["status"] == "VALID"
