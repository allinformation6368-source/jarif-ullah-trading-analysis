from datetime import datetime
from unittest.mock import patch

from data.scanner.scanner_engine import ScannerEngine


def fake_data(symbol, timeframe, outputsize, provider):
    return {
        "source": "cache",
        "candles": [
            {
                "datetime": "2026-10-08 06:00:00",
                "close": 100,
            }
        ],
        "credits_consumed": 0,
        "credit_status": {},
    }


def test_cheap_screen_then_deep():
    engine = ScannerEngine()

    calls = []

    def fake_get(**kwargs):
        calls.append(kwargs["timeframe"])
        return fake_data(**kwargs)

    with patch(
        "data.scanner.scanner_engine.get_market_data",
        side_effect=fake_get,
    ):
        result = engine.next_scan(
            mode="scalping",
            now=datetime(2026, 10, 8, 6, 0, 0),
        )

    assert result["status"] == "SCANNED"
    assert result["pair"] == "BTC/USD"
    assert result["screening_timeframes"] == ("1min", "5min")
    assert result["deeper_timeframes"] == ("15min", "1h")
    assert result["screening_passed"] is True
    assert result["deep_analysis_run"] is True
    assert calls == ["1min", "5min", "15min", "1h"]

    print("test_cheap_screen_then_deep: PASS")


def test_screen_failure_blocks_deep():
    engine = ScannerEngine()

    calls = []

    def fake_get(**kwargs):
        calls.append(kwargs["timeframe"])

        if kwargs["timeframe"] == "5min":
            return {
                "source": "cache",
                "candles": [],
                "credits_consumed": 0,
                "credit_status": {},
            }

        return fake_data(**kwargs)

    with patch(
        "data.scanner.scanner_engine.get_market_data",
        side_effect=fake_get,
    ):
        result = engine.next_scan(
            mode="scalping",
            now=datetime(2026, 10, 8, 6, 0, 0),
        )

    assert result["screening_passed"] is False
    assert result["deep_analysis_run"] is False
    assert calls == ["1min", "5min"]

    print("test_screen_failure_blocks_deep: PASS")


def test_force_deep():
    engine = ScannerEngine()

    calls = []

    def fake_get(**kwargs):
        calls.append(kwargs["timeframe"])
        return fake_data(**kwargs)

    with patch(
        "data.scanner.scanner_engine.get_market_data",
        side_effect=fake_get,
    ):
        result = engine.next_scan(
            mode="intraday",
            force_deep=True,
            now=datetime(2026, 10, 8, 6, 0, 0),
        )

    assert result["deep_analysis_run"] is True
    assert calls == ["5min", "15min", "1h", "4h"]

    print("test_force_deep: PASS")


if __name__ == "__main__":
    test_cheap_screen_then_deep()
    test_screen_failure_blocks_deep()
    test_force_deep()
    print("STEP 6 SCANNER ENGINE TESTS: PASS")
