from datetime import datetime
from types import SimpleNamespace

from data.scanner.runner import ScannerRunner


class FakeRuntime:
    def __init__(self):
        self.stop_called = False
        self.tick_calls = 0

    def status(self):
        return {
            "running": False,
            "scanner_status": "PAUSED",
            "next_pair": "BTC/USD",
            "credits_used_today": 0,
            "credits_remaining": 800,
        }

    def tick(self, mode="scalping", outputsize=100, now=None):
        self.tick_calls += 1
        return {
            "status": "PAUSED",
            "reason": "Fake runtime",
            "interval_seconds": 72,
        }

    def stop(self):
        self.stop_called = True


def test_runner_starts_explicitly():
    runtime = FakeRuntime()
    runner = ScannerRunner(runtime=runtime)

    assert runner.running is False

    status = runner.start()

    assert runner.running is True
    assert status["execution_mode"] == "PAPER"
    assert status["live_execution"] is False

    print("test_runner_starts_explicitly: PASS")


def test_runner_does_not_scan_before_start():
    runtime = FakeRuntime()
    runner = ScannerRunner(runtime=runtime)

    result = runner.tick()

    assert result["status"] == "STOPPED"
    assert runtime.tick_calls == 0

    print("test_runner_does_not_scan_before_start: PASS")


def test_runner_delegates_after_start():
    runtime = FakeRuntime()
    runner = ScannerRunner(runtime=runtime)

    runner.start()
    result = runner.tick(
        mode="scalping",
        now=datetime(2026, 10, 8, 12, 0),
    )

    assert result["status"] == "PAUSED"
    assert result["execution_mode"] == "PAPER"
    assert runtime.tick_calls == 1

    print("test_runner_delegates_after_start: PASS")


def test_runner_stop_calls_runtime_stop():
    runtime = FakeRuntime()
    runner = ScannerRunner(runtime=runtime)

    runner.start()
    runner.stop()

    assert runner.running is False
    assert runtime.stop_called is True

    print("test_runner_stop_calls_runtime_stop: PASS")


def test_live_execution_is_rejected():
    runtime = FakeRuntime()

    try:
        ScannerRunner(
            runtime=runtime,
            execution_mode="LIVE",
        )
    except ValueError as exc:
        assert "LIVE" in str(exc)
    else:
        raise AssertionError("LIVE execution was not rejected")

    print("test_live_execution_is_rejected: PASS")


def test_invalid_scanner_mode_rejected():
    runtime = FakeRuntime()
    runner = ScannerRunner(runtime=runtime)

    runner.start()

    try:
        runner.tick(mode="invalid")
    except ValueError:
        pass
    else:
        raise AssertionError("Invalid mode was not rejected")

    assert runtime.tick_calls == 0

    print("test_invalid_scanner_mode_rejected: PASS")


def test_runner_status_is_read_only():
    runtime = FakeRuntime()
    runner = ScannerRunner(runtime=runtime)

    before = runtime.tick_calls
    status = runner.status()
    after = runtime.tick_calls

    assert before == after
    assert status["live_execution"] is False
    assert status["credits_used_today"] == 0

    print("test_runner_status_is_read_only: PASS")


def test_run_once_requires_started_runner():
    runtime = FakeRuntime()
    runner = ScannerRunner(runtime=runtime)

    result = runner.run_once()

    assert result["status"] == "STOPPED"
    assert runtime.tick_calls == 0

    print("test_run_once_requires_started_runner: PASS")


def test_no_direct_provider_path():
    from pathlib import Path

    source = Path("data/scanner/runner.py").read_text()

    forbidden = (
        "fetch_market_data",
        "twelvedata",
        "requests.get",
        "http.client",
    )

    for item in forbidden:
        assert item not in source

    print("test_no_direct_provider_path: PASS")


def test():
    test_runner_starts_explicitly()
    test_runner_does_not_scan_before_start()
    test_runner_delegates_after_start()
    test_runner_stop_calls_runtime_stop()
    test_live_execution_is_rejected()
    test_invalid_scanner_mode_rejected()
    test_runner_status_is_read_only()
    test_run_once_requires_started_runner()
    test_no_direct_provider_path()

    print("STEP 13E RUNNER TESTS: PASS")


if __name__ == "__main__":
    test()
