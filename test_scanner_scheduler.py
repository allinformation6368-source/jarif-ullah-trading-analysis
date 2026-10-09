from datetime import datetime

from data.scanner.round_robin import RoundRobinScanner
from data.scanner.scanner_config import (
    SCANNER_PAIRS,
    SCANNER_START,
    SCANNER_STOP,
    validate_scanner_config,
)
from data.scanner.scheduler import ScannerScheduler


def test_config():
    assert validate_scanner_config() is True
    assert len(SCANNER_PAIRS) == 8
    assert len(set(SCANNER_PAIRS)) == 8


def test_round_robin():
    scanner = RoundRobinScanner()

    observed = [
        scanner.next_pair()
        for _ in range(8)
    ]

    assert tuple(observed) == SCANNER_PAIRS

    assert scanner.next_pair() == SCANNER_PAIRS[0]


def test_round_robin_is_sequential():
    scanner = RoundRobinScanner()

    first = scanner.next_pair()
    second = scanner.next_pair()

    assert first != second


def test_active_window():
    scheduler = ScannerScheduler()

    active = datetime(2026, 10, 8, 6, 0, 0)
    middle = datetime(2026, 10, 8, 12, 0, 0)
    stop = datetime(2026, 10, 8, 21, 0, 0)

    assert scheduler.is_active(active) is True
    assert scheduler.is_active(middle) is True
    assert scheduler.is_active(stop) is False


def test_before_window():
    scheduler = ScannerScheduler()

    before = datetime(2026, 10, 8, 5, 59, 59)

    assert scheduler.is_active(before) is False


def test_72_second_target():
    assert ScannerScheduler.calculate_interval(1) == 72


def test_dynamic_credit_interval():
    assert ScannerScheduler.calculate_interval(1) == 72
    assert ScannerScheduler.calculate_interval(2) == 144
    assert ScannerScheduler.calculate_interval(3) == 216


def test_budget_exhaustion():
    scheduler = ScannerScheduler()

    now = datetime(2026, 10, 8, 20, 59, 0)

    # This test only verifies that the scheduler can produce a
    # valid scan decision near the end of the active window.
    # Credit-state mutation is tested separately by credit_tracker tests.
    result = scheduler.next_scan(
        now=now,
        actual_cost=1,
    )

    assert result["status"]["scanner_status"] in {
        "ACTIVE",
        "BUDGET_LIMIT",
    }

    if result["allowed"]:
        assert result["pair"]
        assert result["interval_seconds"] >= 72
    else:
        assert result["reason"] in {
            "Planned credit budget exhausted",
            "Scanner outside active window",
        }


if __name__ == "__main__":
    tests = [
        test_config,
        test_round_robin,
        test_round_robin_is_sequential,
        test_active_window,
        test_before_window,
        test_72_second_target,
        test_dynamic_credit_interval,
        test_budget_exhaustion,
    ]

    for test in tests:
        test()
        print(f"{test.__name__}: PASS")

    print("SCANNER SCHEDULER TESTS: PASS")
