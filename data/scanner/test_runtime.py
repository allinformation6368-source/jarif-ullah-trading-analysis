from datetime import datetime, time

from data.scanner.runtime import ScannerRuntime


class FakeScheduler:
    def __init__(self):
        self.pair = "BTC/USD"

    def status(self, now=None):
        if now is not None and now.time() >= time(21, 0):
            scanner_status = "PAUSED"
        elif now is not None and now.time() < time(6, 0):
            scanner_status = "PAUSED"
        else:
            scanner_status = "ACTIVE"

        return {
            "scanner_status": scanner_status,
            "next_pair": self.pair,
            "planned_budget": 750,
            "safety_reserve": 50,
            "credits_used_today": 0,
            "credits_remaining": 800,
            "remaining_planned_budget": 750,
        }


class FakeEngine:
    def __init__(self):
        self.scheduler = FakeScheduler()
        self.calls = 0
        self.last_result = None

    def status(self):
        return {
            "pairs": [
                "BTC/USD",
                "ETH/USD",
                "EUR/USD",
                "GBP/USD",
                "USD/JPY",
                "USD/CHF",
                "AUD/USD",
                "USD/CAD",
            ],
            "scans_completed": self.calls,
            "last_result": self.last_result,
            "active_setups": {},
            "scheduler": self.scheduler.status(),
        }

    def next_scan(self, **kwargs):
        self.calls += 1

        result = {
            "status": "SCANNED",
            "pair": "BTC/USD",
            "interval_seconds": 72,
            "credits_consumed": 1,
            "scans_completed": self.calls,
        }

        self.last_result = result
        return result


def active_time():
    return datetime(2026, 10, 8, 12, 0, 0)


def test_first_tick_scans_once():
    engine = FakeEngine()
    runtime = ScannerRuntime(engine=engine)

    result = runtime.tick(now=active_time())

    assert result["status"] == "SCANNED"
    assert engine.calls == 1
    assert runtime.next_run_at is not None


def test_second_tick_waits_until_due():
    engine = FakeEngine()
    runtime = ScannerRuntime(engine=engine)

    first = active_time()
    runtime.tick(now=first)

    result = runtime.tick(
        now=first.replace(second=30),
    )

    assert result["status"] == "WAITING"
    assert engine.calls == 1


def test_due_tick_runs_again():
    engine = FakeEngine()
    runtime = ScannerRuntime(engine=engine)

    first = active_time()
    runtime.tick(now=first)

    second = first.replace(minute=1, second=12)

    result = runtime.tick(now=second)

    assert result["status"] == "SCANNED"
    assert engine.calls == 2


def test_runtime_does_not_scan_outside_window():
    engine = FakeEngine()
    runtime = ScannerRuntime(engine=engine)

    outside = datetime(
        2026,
        10,
        8,
        21,
        0,
        0,
    )

    result = runtime.tick(now=outside)

    assert result["status"] == "PAUSED"
    assert engine.calls == 0
    assert runtime.running is False


def test_runtime_status_is_read_only():
    engine = FakeEngine()
    runtime = ScannerRuntime(engine=engine)

    status = runtime.status(now=active_time())

    assert status["next_pair"] == "BTC/USD"
    assert status["credits_used_today"] == 0
    assert status["credits_remaining"] == 800
    assert engine.calls == 0


def test_runtime_uses_engine_interval():
    engine = FakeEngine()
    runtime = ScannerRuntime(engine=engine)

    first = active_time()
    runtime.tick(now=first)

    delta = runtime.next_run_at - first

    assert delta.total_seconds() == 72


def test_no_direct_provider_path():
    source = open("data/scanner/runtime.py", encoding="utf-8").read()

    assert "fetch_market_data" not in source
    assert "twelvedata" not in source
    assert "requests.get" not in source
    assert "http.client" not in source


if __name__ == "__main__":
    tests = [
        test_first_tick_scans_once,
        test_second_tick_waits_until_due,
        test_due_tick_runs_again,
        test_runtime_does_not_scan_outside_window,
        test_runtime_status_is_read_only,
        test_runtime_uses_engine_interval,
        test_no_direct_provider_path,
    ]

    for test in tests:
        test()
        print(f"{test.__name__}: PASS")

    print("STEP 13D RUNTIME TESTS: PASS")
