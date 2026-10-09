from datetime import datetime, timedelta

from data.scanner.scanner_engine import ScannerEngine


class ScannerRuntime:
    """
    Thin runtime loop around ScannerEngine.

    Responsibilities:
    - keep one persistent ScannerEngine instance
    - enforce local next-run timing
    - stop normal scanning outside 06:00-21:00
    - never call the provider directly
    - never create a second scheduler
    """

    def __init__(self, engine=None):
        self.engine = engine or ScannerEngine()
        self.next_run_at = None
        self.last_result = None
        self.running = False

    def status(self, now=None):
        now = now or datetime.now()

        engine_status = self.engine.status()
        scheduler = engine_status.get("scheduler", {})

        return {
            "running": self.running,
            "next_run_at": (
                self.next_run_at.isoformat()
                if self.next_run_at
                else None
            ),
            "last_result": self.last_result,
            "engine": engine_status,
            "scanner_status": scheduler.get(
                "scanner_status",
                "PAUSED",
            ),
            "next_pair": scheduler.get(
                "next_pair",
            ),
            "credits_used_today": scheduler.get(
                "credits_used_today",
                0,
            ),
            "credits_remaining": scheduler.get(
                "credits_remaining",
                800,
            ),
            "remaining_planned_budget": scheduler.get(
                "remaining_planned_budget",
                0,
            ),
        }

    def tick(
        self,
        mode="scalping",
        outputsize=100,
        now=None,
        force_deep=False,
    ):
        """
        Execute at most one scanner cycle when due.

        Tests can inject `now` and a fake engine.
        """
        now = now or datetime.now()

        scheduler = self.engine.scheduler.status(now=now)

        if scheduler["scanner_status"] != "ACTIVE":
            self.running = False
            return {
                "status": "PAUSED",
                "reason": "Scanner outside active window",
                "scheduler": scheduler,
            }

        self.running = True

        if self.next_run_at is not None and now < self.next_run_at:
            return {
                "status": "WAITING",
                "reason": "Next scan not due",
                "next_run_at": self.next_run_at.isoformat(),
                "scheduler": scheduler,
            }

        result = self.engine.next_scan(
            mode=mode,
            outputsize=outputsize,
            now=now,
            force_deep=force_deep,
        )

        self.last_result = result

        # Engine scheduler is the authority for the safe interval.
        interval = int(
            result.get("interval_seconds", 72) or 72
        )

        # A skipped scan outside the active window must not schedule
        # another request.
        if result.get("status") == "SKIPPED":
            self.running = False
            self.next_run_at = None
            return result

        self.next_run_at = now + timedelta(seconds=interval)

        return result

    def stop(self):
        """
        Stop the runtime loop without changing credit state.
        """
        self.running = False
        self.next_run_at = None

    def run_forever(
        self,
        mode="scalping",
        outputsize=100,
        sleep_fn=None,
        now_fn=None,
    ):
        """
        Production loop.

        `sleep_fn` and `now_fn` are injectable for deterministic tests.
        """
        import time

        if sleep_fn is None:
            sleep_fn = time.sleep

        if now_fn is None:
            now_fn = datetime.now

        self.running = True

        while self.running:
            now = now_fn()

            result = self.tick(
                mode=mode,
                outputsize=outputsize,
                now=now,
            )

            if result.get("status") == "PAUSED":
                self.running = False
                break

            if self.next_run_at is None:
                continue

            delay = max(
                0,
                (self.next_run_at - now).total_seconds(),
            )

            sleep_fn(min(delay, 5))


__all__ = ["ScannerRuntime"]
