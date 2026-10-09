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


def test_setup_candidates_are_persisted():
    engine = ScannerEngine()

    with patch(
        "data.scanner.scanner_engine.get_market_data",
        side_effect=fake_data,
    ):
        result = engine.next_scan(
            mode="scalping",
            now=datetime(2026, 10, 8, 6, 0, 0),
        )

    # Simulate a future strategy layer supplying a setup.
    result["setup_candidates"] = [
        {
            "setup_id": "test-setup",
            "candle_id": "2026-10-08T06:00:00",
            "metadata": {"source": "test"},
            "ttl_seconds": 300,
        }
    ]

    # Feed the candidate through the same persistence contract.
    persisted = engine.setup_persistence.observe(
        pair=result["pair"],
        mode=result["mode"],
        setup_id="test-setup",
        candle_id="2026-10-08T06:00:00",
        metadata={"source": "test"},
        ttl_seconds=300,
        now=result["timestamp"],
    )

    assert persisted["state"] == "NEW"
    assert persisted["setup_id"] == "test-setup"

    status = engine.status()
    assert len(status["active_setups"]) == 1

    print("test_setup_candidates_are_persisted: PASS")


def test_setup_persists_across_engine_scans():
    engine = ScannerEngine()

    first = engine.setup_persistence.observe(
        pair="BTC/USD",
        mode="scalping",
        setup_id="persistent-setup",
        candle_id="candle-1",
        now="2026-10-08T06:00:00+00:00",
    )

    second = engine.setup_persistence.observe(
        pair="BTC/USD",
        mode="scalping",
        setup_id="persistent-setup",
        candle_id="candle-2",
        now="2026-10-08T06:02:00+00:00",
    )

    assert first["state"] == "NEW"
    assert second["state"] == "PERSISTING"
    assert second["observations"] == 2

    print("test_setup_persists_across_engine_scans: PASS")


if __name__ == "__main__":
    test_setup_candidates_are_persisted()
    test_setup_persists_across_engine_scans()
    print("STEP 8B SCANNER TESTS: PASS")
