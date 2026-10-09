from datetime import datetime
from unittest.mock import patch

from data.scanner.scanner_engine import ScannerEngine
from data.scanner.scanner_config import SCANNER_PAIRS


def test_engine_config():
    engine = ScannerEngine()
    assert len(SCANNER_PAIRS) == 8
    assert engine.status()["pairs"] == list(SCANNER_PAIRS)
    print("test_engine_config: PASS")


def test_engine_outside_window():
    engine = ScannerEngine()

    result = engine.next_scan(
        now=datetime(2026, 10, 8, 22, 0, 0)
    )

    assert result["status"] == "SKIPPED"
    assert result["reason"] == "Scanner outside active window"

    print("test_engine_outside_window: PASS")


def test_engine_uses_market_data_layer():
    engine = ScannerEngine()

    fake_data = {
        "source": "cache",
        "candles": [{"datetime": "2026-10-08 06:00:00", "close": 100}],
        "credits_consumed": 0,
        "credit_status": {
            "credits_used_today": 0,
            "credits_remaining": 800,
            "remaining_planned_budget": 750,
        },
    }

    with patch(
        "data.scanner.scanner_engine.get_market_data",
        return_value=fake_data,
    ) as mocked:

        result = engine.next_scan(
            timeframe="1min",
            now=datetime(2026, 10, 8, 6, 0, 0),
        )

    assert result["status"] == "SCANNED"
    assert result["pair"] == "BTC/USD"
    assert result["source"] == "cache"
    assert result["credits_consumed"] == 0
    # Step 6 intentionally performs screening + deeper timeframe fetches.
    assert mocked.call_count == 4

    intervals = [
        call.kwargs["timeframe"]
        for call in mocked.call_args_list
    ]

    assert intervals == ["1min", "5min", "15min", "1h"]

    print("test_engine_uses_market_data_layer: PASS")


def test_engine_sequential_pairs():
    engine = ScannerEngine()

    fake_data = {
        "source": "cache",
        "candles": [],
        "credits_consumed": 0,
        "credit_status": {},
    }

    results = []

    with patch(
        "data.scanner.scanner_engine.get_market_data",
        return_value=fake_data,
    ):
        for _ in range(8):
            result = engine.next_scan(
                timeframe="1min",
                now=datetime(2026, 10, 8, 6, 0, 0),
            )
            results.append(result["pair"])

    assert results == list(SCANNER_PAIRS)

    print("test_engine_sequential_pairs: PASS")


def test_engine_never_directly_calls_provider():
    import inspect
    import data.scanner.scanner_engine as module

    source = inspect.getsource(module)

    assert "twelve_data" not in source.lower()
    assert "TwelveDataClient" not in source

    print("test_engine_no_direct_provider_call: PASS")


if __name__ == "__main__":
    tests = [
        test_engine_config,
        test_engine_outside_window,
        test_engine_uses_market_data_layer,
        test_engine_sequential_pairs,
        test_engine_never_directly_calls_provider,
    ]

    for test in tests:
        test()

    print("SCANNER ENGINE TESTS: PASS")
