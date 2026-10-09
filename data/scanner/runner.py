from datetime import datetime

from data.scanner.runtime import ScannerRuntime


class ScannerRunner:
    """
    Explicitly controlled scanner runner.

    - Never starts automatically.
    - PAPER/SAFE only.
    - Delegates market scheduling to ScannerRuntime/ScannerScheduler.
    - Does not call TwelveData directly.
    """

    ALLOWED_MODES = {"scalping", "intraday", "swing"}
    SAFE_MODES = {"PAPER", "SAFE"}

    def __init__(self, runtime=None, execution_mode="PAPER"):
        execution_mode = str(execution_mode).upper()

        if execution_mode not in self.SAFE_MODES:
            raise ValueError("LIVE execution is disabled")

        self.runtime = runtime or ScannerRuntime()
        self.execution_mode = execution_mode
        self.running = False

    def start(self):
        self.running = True
        return self.status()

    def stop(self):
        self.running = False
        self.runtime.stop()
        return self.status()

    def tick(self, mode="scalping", outputsize=100, now=None):
        if mode not in self.ALLOWED_MODES:
            raise ValueError(f"Unsupported scanner mode: {mode}")

        if not self.running:
            return {
                "status": "STOPPED",
                "reason": "Runner is not started",
                "execution_mode": self.execution_mode,
            }

        result = self.runtime.tick(
            mode=mode,
            outputsize=outputsize,
            now=now,
        )

        result["execution_mode"] = self.execution_mode
        return result

    def status(self):
        runtime_status = self.runtime.status()
        return {
            "running": self.running,
            "execution_mode": self.execution_mode,
            "live_execution": False,
            "runtime": runtime_status,
            "scanner_status": runtime_status.get("scanner_status"),
            "next_pair": runtime_status.get("next_pair"),
            "credits_used_today": runtime_status.get(
                "credits_used_today", 0
            ),
            "credits_remaining": runtime_status.get(
                "credits_remaining", 800
            ),
        }

    def run_once(self, mode="scalping", outputsize=100, now=None):
        """
        Explicit one-shot execution.

        The runner must already be started. No background loop is
        created by this method.
        """
        return self.tick(
            mode=mode,
            outputsize=outputsize,
            now=now,
        )


__all__ = ["ScannerRunner"]
