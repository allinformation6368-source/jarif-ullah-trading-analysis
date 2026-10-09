import json
import tempfile
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

import data.scanner.cli as cli
import data.scanner.control_state as control


class FakeRunner:
    def __init__(self):
        self.started = False
        self.stopped = False
        self.tick_calls = 0

    def status(self):
        return {
            "running": self.started,
            "execution_mode": "PAPER",
            "live_execution": False,
        }

    def start(self):
        self.started = True
        return self.status()

    def stop(self):
        self.started = False
        self.stopped = True
        return self.status()

    def tick(self, mode="scalping", outputsize=100, now=None):
        self.tick_calls += 1

        return {
            "status": "SCANNED",
            "mode": mode,
            "outputsize": outputsize,
            "execution_mode": "PAPER",
            "live_execution": False,
        }


def call(args, runner=None):
    output = StringIO()

    with redirect_stdout(output):
        code = cli.main(args, runner=runner)

    return code, json.loads(output.getvalue())


def isolated_state():
    tmp = tempfile.TemporaryDirectory()

    control.STATE_DIR = Path(tmp.name)
    control.STATE_FILE = (
        control.STATE_DIR / "runner_control.json"
    )

    return tmp


def test_status_does_not_scan():
    tmp = isolated_state()

    try:
        runner = FakeRunner()

        code, result = call(
            ["status"],
            runner=runner,
        )

        assert code == 0
        assert result["running"] is False
        assert runner.tick_calls == 0

    finally:
        tmp.cleanup()

    print("test_status_does_not_scan: PASS")


def test_start_persists_running_state():
    tmp = isolated_state()

    try:
        runner = FakeRunner()

        code, result = call(
            [
                "start",
                "--mode",
                "scalping",
                "--outputsize",
                "100",
            ],
            runner=runner,
        )

        assert code == 0
        assert result["state"]["running"] is True
        assert control.load_state()["running"] is True
        assert runner.started is True
        assert runner.tick_calls == 0

    finally:
        tmp.cleanup()

    print("test_start_persists_running_state: PASS")


def test_tick_blocked_when_stopped():
    tmp = isolated_state()

    try:
        runner = FakeRunner()

        code, result = call(
            ["tick"],
            runner=runner,
        )

        assert code == 0
        assert result["status"] == "STOPPED"
        assert runner.tick_calls == 0

    finally:
        tmp.cleanup()

    print("test_tick_blocked_when_stopped: PASS")


def test_tick_allowed_when_persisted_running():
    tmp = isolated_state()

    try:
        runner = FakeRunner()

        call(["start"], runner=runner)

        code, result = call(
            ["tick"],
            runner=runner,
        )

        assert code == 0
        assert result["result"]["status"] == "SCANNED"
        assert runner.tick_calls == 1

    finally:
        tmp.cleanup()

    print("test_tick_allowed_when_persisted_running: PASS")


def test_stop_persists_stopped_state():
    tmp = isolated_state()

    try:
        runner = FakeRunner()

        call(["start"], runner=runner)

        code, result = call(
            ["stop"],
            runner=runner,
        )

        assert code == 0
        assert result["state"]["running"] is False
        assert control.load_state()["running"] is False
        assert runner.stopped is True
        assert runner.tick_calls == 0

    finally:
        tmp.cleanup()

    print("test_stop_persists_stopped_state: PASS")


def test_start_then_status():
    tmp = isolated_state()

    try:
        runner = FakeRunner()

        call(["start"], runner=runner)

        code, result = call(
            ["status"],
            runner=runner,
        )

        assert code == 0
        assert result["running"] is True
        assert result["mode"] == "scalping"
        assert result["outputsize"] == 100
        assert runner.tick_calls == 0

    finally:
        tmp.cleanup()

    print("test_start_then_status: PASS")


def test_start_stop_tick_is_blocked():
    tmp = isolated_state()

    try:
        runner = FakeRunner()

        call(["start"], runner=runner)
        call(["stop"], runner=runner)

        code, result = call(
            ["tick"],
            runner=runner,
        )

        assert code == 0
        assert result["status"] == "STOPPED"
        assert runner.tick_calls == 0

    finally:
        tmp.cleanup()

    print("test_start_stop_tick_is_blocked: PASS")


def test_live_state_rejected():
    tmp = isolated_state()

    try:
        control.STATE_FILE.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        control.STATE_FILE.write_text(
            json.dumps(
                {
                    "running": False,
                    "execution_mode": "LIVE",
                    "mode": "scalping",
                    "outputsize": 100,
                }
            )
        )

        try:
            call(["status"])
        except ValueError:
            pass
        else:
            raise AssertionError(
                "LIVE execution was not rejected"
            )

    finally:
        tmp.cleanup()

    print("test_live_state_rejected: PASS")


def test_no_direct_provider():
    source = Path(
        "data/scanner/cli.py"
    ).read_text()

    forbidden = (
        "fetch_market_data",
        "twelvedata",
        "requests.get",
        "http.client",
        "place_order",
        "execute_order",
    )

    for item in forbidden:
        assert item not in source

    print("test_cli_no_direct_provider: PASS")


def test():
    test_status_does_not_scan()
    test_start_persists_running_state()
    test_tick_blocked_when_stopped()
    test_tick_allowed_when_persisted_running()
    test_stop_persists_stopped_state()
    test_start_then_status()
    test_start_stop_tick_is_blocked()
    test_live_state_rejected()
    test_no_direct_provider()

    print("STEP 13H CLI INTEGRATION TESTS: PASS")


if __name__ == "__main__":
    test()
