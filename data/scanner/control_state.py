import json
from pathlib import Path
from threading import RLock


STATE_DIR = Path(".runtime/scanner")
STATE_FILE = STATE_DIR / "runner_control.json"

_lock = RLock()


def _default_state():
    return {
        "running": False,
        "execution_mode": "PAPER",
        "mode": "scalping",
        "outputsize": 100,
    }


def load_state():
    with _lock:
        if not STATE_FILE.exists():
            return _default_state()

        try:
            data = json.loads(STATE_FILE.read_text())
        except (OSError, ValueError, TypeError):
            return _default_state()

        state = _default_state()
        state.update(data)

        state["running"] = bool(state["running"])
        state["execution_mode"] = str(
            state["execution_mode"]
        ).upper()

        if state["execution_mode"] == "LIVE":
            raise ValueError("LIVE execution is disabled")

        if state["execution_mode"] not in {"PAPER", "SAFE"}:
            state["execution_mode"] = "PAPER"

        state["mode"] = str(state["mode"])
        state["outputsize"] = int(state["outputsize"])

        return state


def save_state(**updates):
    with _lock:
        state = load_state()
        state.update(updates)

        if state["execution_mode"].upper() == "LIVE":
            raise ValueError("LIVE execution is disabled")

        STATE_DIR.mkdir(parents=True, exist_ok=True)

        temp_file = STATE_FILE.with_suffix(".tmp")
        temp_file.write_text(
            json.dumps(state, indent=2, sort_keys=True)
        )
        temp_file.replace(STATE_FILE)

        return state


def set_running(running):
    return save_state(running=bool(running))


def is_running():
    return bool(load_state()["running"])


def clear_state():
    with _lock:
        if STATE_FILE.exists():
            STATE_FILE.unlink()

        return _default_state()


__all__ = [
    "STATE_DIR",
    "STATE_FILE",
    "load_state",
    "save_state",
    "set_running",
    "is_running",
    "clear_state",
]
