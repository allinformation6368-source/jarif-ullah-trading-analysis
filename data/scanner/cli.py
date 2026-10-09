import argparse
import json
from datetime import datetime

from data.scanner.control_state import load_state, save_state
from data.scanner.runner import ScannerRunner


def build_parser():
    parser = argparse.ArgumentParser(
        description="Controlled PAPER/SAFE scanner CLI"
    )

    parser.add_argument(
        "command",
        choices=("status", "start", "tick", "stop"),
    )

    parser.add_argument(
        "--mode",
        choices=("scalping", "intraday", "swing"),
        default=None,
    )

    parser.add_argument(
        "--outputsize",
        type=int,
        default=None,
    )

    return parser


def _safe_state():
    state = load_state()

    if state.get("execution_mode", "PAPER").upper() == "LIVE":
        raise ValueError("LIVE execution is disabled")

    return state


def main(argv=None, runner=None, now=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    state = _safe_state()

    # STATUS: read-only. Never scans.
    if args.command == "status":
        result = {
            "command": "status",
            "running": state["running"],
            "execution_mode": state["execution_mode"],
            "mode": state["mode"],
            "outputsize": state["outputsize"],
            "live_execution": False,
        }

        if runner is not None:
            result["runner"] = runner.status()

        print(json.dumps(result, indent=2, sort_keys=True, default=str))
        return 0

    # START: local state only. Never scans.
    if args.command == "start":
        mode = args.mode or state["mode"]
        outputsize = args.outputsize or state["outputsize"]

        if mode not in {"scalping", "intraday", "swing"}:
            raise ValueError(f"Unsupported scanner mode: {mode}")

        state = save_state(
            running=True,
            execution_mode="PAPER",
            mode=mode,
            outputsize=outputsize,
        )

        if runner is not None:
            result = runner.start()
        else:
            result = {
                "running": True,
                "execution_mode": "PAPER",
                "live_execution": False,
            }

        result = {
            "command": "start",
            "state": state,
            "runner": result,
        }

        print(json.dumps(result, indent=2, sort_keys=True, default=str))
        return 0

    # STOP: local state only + runner stop. Never scans.
    if args.command == "stop":
        state = save_state(running=False)

        if runner is not None:
            result = runner.stop()
        else:
            result = {
                "running": False,
                "execution_mode": state["execution_mode"],
                "live_execution": False,
            }

        result = {
            "command": "stop",
            "state": state,
            "runner": result,
        }

        print(json.dumps(result, indent=2, sort_keys=True, default=str))
        return 0

    # TICK: explicit scan only when persisted state says RUNNING.
    if args.command == "tick":
        if not state["running"]:
            result = {
                "command": "tick",
                "status": "STOPPED",
                "reason": "Persistent scanner state is STOPPED",
                "execution_mode": state["execution_mode"],
                "live_execution": False,
            }

            print(
                json.dumps(
                    result,
                    indent=2,
                    sort_keys=True,
                    default=str,
                )
            )
            return 0

        mode = args.mode or state["mode"]
        outputsize = args.outputsize or state["outputsize"]

        if runner is None:
            runner = ScannerRunner()
            runner.start()

        result = runner.tick(
            mode=mode,
            outputsize=outputsize,
            now=now,
        )

        print(
            json.dumps(
                {
                    "command": "tick",
                    "result": result,
                    "execution_mode": "PAPER",
                    "live_execution": False,
                },
                indent=2,
                sort_keys=True,
                default=str,
            )
        )
        return 0

    parser.error("Unsupported command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
