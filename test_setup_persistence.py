from datetime import datetime, timezone

from data.scanner.setup_persistence import SetupPersistence


BASE = datetime(2026, 10, 8, 6, 0, 0, tzinfo=timezone.utc)


def test_new_setup():
    tracker = SetupPersistence(default_ttl_seconds=300)

    result = tracker.observe(
        "BTC/USD",
        "scalping",
        "setup-1",
        "candle-1",
        now=BASE,
    )

    assert result["state"] == "NEW"
    assert result["observations"] == 1

    print("test_new_setup: PASS")


def test_setup_persists():
    tracker = SetupPersistence(default_ttl_seconds=300)

    first = tracker.observe(
        "BTC/USD",
        "scalping",
        "setup-1",
        "candle-1",
        now=BASE,
    )

    second = tracker.observe(
        "BTC/USD",
        "scalping",
        "setup-1",
        "candle-2",
        now=BASE.replace(minute=2),
    )

    assert first["state"] == "NEW"
    assert second["state"] == "PERSISTING"
    assert second["observations"] == 2
    assert second["last_candle_id"] == "candle-2"

    print("test_setup_persists: PASS")


def test_setup_expires():
    tracker = SetupPersistence(default_ttl_seconds=300)

    tracker.observe(
        "BTC/USD",
        "scalping",
        "setup-1",
        "candle-1",
        now=BASE,
    )

    result = tracker.get(
        "BTC/USD",
        "scalping",
        "setup-1",
        now=BASE.replace(minute=6),
    )

    assert result is None

    print("test_setup_expires: PASS")


def test_setup_isolated_by_pair_mode_and_id():
    tracker = SetupPersistence(default_ttl_seconds=300)

    tracker.observe(
        "BTC/USD",
        "scalping",
        "setup-1",
        "candle-1",
        now=BASE,
    )

    assert tracker.get(
        "BTC/USD",
        "scalping",
        "setup-1",
        now=BASE,
    ) is not None

    assert tracker.get(
        "ETH/USD",
        "scalping",
        "setup-1",
        now=BASE,
    ) is None

    assert tracker.get(
        "BTC/USD",
        "intraday",
        "setup-1",
        now=BASE,
    ) is None

    assert tracker.get(
        "BTC/USD",
        "scalping",
        "setup-2",
        now=BASE,
    ) is None

    print("test_setup_isolated_by_pair_mode_and_id: PASS")


def test_invalidate():
    tracker = SetupPersistence(default_ttl_seconds=300)

    tracker.observe(
        "BTC/USD",
        "scalping",
        "setup-1",
        "candle-1",
        now=BASE,
    )

    assert tracker.invalidate(
        "BTC/USD",
        "scalping",
        "setup-1",
    ) is True

    assert tracker.get(
        "BTC/USD",
        "scalping",
        "setup-1",
        now=BASE,
    ) is None

    print("test_invalidate: PASS")


if __name__ == "__main__":
    test_new_setup()
    test_setup_persists()
    test_setup_expires()
    test_setup_isolated_by_pair_mode_and_id()
    test_invalidate()
    print("STEP 8 SETUP PERSISTENCE TESTS: PASS")
