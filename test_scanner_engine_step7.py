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


def test_first_scan_processes_new_candles():
    engine = ScannerEngine()

    with patch(
        "data.scanner.scanner_engine.get_market_data",
        side_effect=fake_data,
    ):
        result = engine.next_scan(
            mode="scalping",
            now=datetime(2026, 10, 8, 6, 0, 0),
        )

    assert result["status"] == "SCANNED"
    assert result["screening_passed"] is True
    assert len(result["fresh_candles"]) == 4

    print("test_first_scan_processes_new_candles: PASS")


def test_duplicate_candles_block_processing():
    engine = ScannerEngine()

    with patch(
        "data.scanner.scanner_engine.get_market_data",
        side_effect=fake_data,
    ):
        first = engine.next_scan(
            mode="scalping",
            now=datetime(2026, 10, 8, 6, 0, 0),
        )

        # Reset scheduler to make a second scan deterministic.
        engine.scheduler.scanner.reset()

        second = engine.next_scan(
            mode="scalping",
            now=datetime(2026, 10, 8, 6, 1, 0),
        )

    assert first["screening_passed"] is True
    assert second["screening_passed"] is True
    assert second["screening_fresh"] is False
    assert second["deep_analysis_run"] is False
    assert len(second["duplicate_or_stale"]) == 2

    print("test_duplicate_candles_block_processing: PASS")


if __name__ == "__main__":
    test_first_scan_processes_new_candles()
    test_duplicate_candles_block_processing()
    print("STEP 7 SCANNER TESTS: PASS")
