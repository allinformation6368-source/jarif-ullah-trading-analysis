from data.scanner.candle_guard import (
    CandleGuard,
    latest_candle_id,
)


def candle(ts, close=100):
    return {
        "datetime": ts,
        "close": close,
    }


def test_latest_candle():
    candles = [
        candle("2026-10-08 06:00:00"),
        candle("2026-10-08 06:01:00"),
        candle("2026-10-08 06:02:00"),
    ]

    assert latest_candle_id(candles) is not None
    print("test_latest_candle: PASS")


def test_new_then_duplicate():
    guard = CandleGuard()

    candles = [candle("2026-10-08 06:00:00")]

    first = guard.check("BTC/USD", "1min", candles)
    assert first["status"] == "NEW"
    assert first["process"] is True

    assert guard.mark_processed("BTC/USD", "1min", candles)

    second = guard.check("BTC/USD", "1min", candles)
    assert second["status"] == "DUPLICATE"
    assert second["process"] is False

    print("test_new_then_duplicate: PASS")


def test_newer_candle():
    guard = CandleGuard()

    first = [candle("2026-10-08 06:00:00")]
    newer = [candle("2026-10-08 06:01:00")]

    guard.mark_processed("BTC/USD", "1min", first)

    result = guard.check("BTC/USD", "1min", newer)

    assert result["status"] == "NEW"
    assert result["process"] is True

    print("test_newer_candle: PASS")


def test_older_candle():
    guard = CandleGuard()

    current = [candle("2026-10-08 06:02:00")]
    older = [candle("2026-10-08 06:01:00")]

    guard.mark_processed("BTC/USD", "1min", current)

    result = guard.check("BTC/USD", "1min", older)

    assert result["status"] == "STALE"
    assert result["process"] is False

    print("test_older_candle: PASS")


def test_timeframe_isolated():
    guard = CandleGuard()

    candles = [candle("2026-10-08 06:00:00")]

    guard.mark_processed("BTC/USD", "1min", candles)

    result = guard.check("BTC/USD", "5min", candles)

    assert result["status"] == "NEW"
    assert result["process"] is True

    print("test_timeframe_isolated: PASS")


if __name__ == "__main__":
    test_latest_candle()
    test_new_then_duplicate()
    test_newer_candle()
    test_older_candle()
    test_timeframe_isolated()
    print("CANDLE GUARD TESTS: PASS")
