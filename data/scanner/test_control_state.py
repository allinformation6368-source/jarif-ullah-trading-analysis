import json
import tempfile
from pathlib import Path

import data.scanner.control_state as control


def test_default_state():
    with tempfile.TemporaryDirectory() as tmp:
        control.STATE_DIR = Path(tmp)
        control.STATE_FILE = control.STATE_DIR / "runner_control.json"

        state = control.load_state()

        assert state["running"] is False
        assert state["execution_mode"] == "PAPER"
        assert state["mode"] == "scalping"

    print("test_default_state: PASS")


def test_state_persists():
    with tempfile.TemporaryDirectory() as tmp:
        control.STATE_DIR = Path(tmp)
        control.STATE_FILE = control.STATE_DIR / "runner_control.json"

        control.set_running(True)

        state = control.load_state()

        assert state["running"] is True
        assert control.is_running() is True

    print("test_state_persists: PASS")


def test_state_survives_reload():
    with tempfile.TemporaryDirectory() as tmp:
        control.STATE_DIR = Path(tmp)
        control.STATE_FILE = control.STATE_DIR / "runner_control.json"

        control.save_state(
            running=True,
            mode="intraday",
            outputsize=50,
        )

        state = json.loads(
            control.STATE_FILE.read_text()
        )

        assert state["running"] is True
        assert state["mode"] == "intraday"
        assert state["outputsize"] == 50

    print("test_state_survives_reload: PASS")


def test_live_is_rejected():
    with tempfile.TemporaryDirectory() as tmp:
        control.STATE_DIR = Path(tmp)
        control.STATE_FILE = control.STATE_DIR / "runner_control.json"

        try:
            control.save_state(
                execution_mode="LIVE"
            )
        except ValueError:
            pass
        else:
            raise AssertionError(
                "LIVE execution was not rejected"
            )

    print("test_live_is_rejected: PASS")


def test_clear_state():
    with tempfile.TemporaryDirectory() as tmp:
        control.STATE_DIR = Path(tmp)
        control.STATE_FILE = control.STATE_DIR / "runner_control.json"

        control.set_running(True)

        assert control.STATE_FILE.exists()

        state = control.clear_state()

        assert state["running"] is False
        assert not control.STATE_FILE.exists()

    print("test_clear_state: PASS")


def test_no_provider_path():
    source = Path(
        "data/scanner/control_state.py"
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

    print("test_no_provider_path: PASS")


def test():
    test_default_state()
    test_state_persists()
    test_state_survives_reload()
    test_live_is_rejected()
    test_clear_state()
    test_no_provider_path()

    print("STEP 13G CONTROL STATE TESTS: PASS")


if __name__ == "__main__":
    test()
