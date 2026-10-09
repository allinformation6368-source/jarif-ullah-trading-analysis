from datetime import datetime, time

from data.scanner.credit_tracker import get_credit_status
from data.scanner.scanner_config import (
    MAX_SCAN_INTERVAL_SECONDS,
    MIN_SCAN_INTERVAL_SECONDS,
    PAIR_SCAN_INTERVAL_SECONDS,
    PLANNED_BUDGET,
    SCANNER_START,
    SCANNER_STOP,
)
from data.scanner.round_robin import RoundRobinScanner


class ScannerScheduler:
    """
    Credit-aware sequential scheduler.

    The scheduler decides whether another pair scan is allowed and
    computes a safe interval from the remaining planned budget.

    It does not make network requests itself.
    """

    def __init__(self, scanner=None):
        self.scanner = scanner or RoundRobinScanner()

    @staticmethod
    def is_active(now=None):
        current = now or datetime.now()

        current_time = current.time()

        return SCANNER_START <= current_time < SCANNER_STOP

    @staticmethod
    def seconds_until_stop(now=None):
        current = now or datetime.now()

        stop = datetime.combine(
            current.date(),
            SCANNER_STOP,
            tzinfo=current.tzinfo,
        )

        seconds = (stop - current).total_seconds()

        return max(0, int(seconds))

    @staticmethod
    def calculate_interval(
        actual_cost=1,
        remaining_budget=None,
        remaining_seconds=None,
    ):
        """
        Calculate a credit-safe interval.

        At 1 credit/scan:
            750 scans / 900 minutes
            = 72 sec/scan.

        If actual average cost rises, interval increases.

        Example:
            1 credit -> 72 sec
            2 credits -> 144 sec
            3 credits -> 216 sec
        """

        if not isinstance(actual_cost, int) or actual_cost <= 0:
            actual_cost = 1

        interval = PAIR_SCAN_INTERVAL_SECONDS * actual_cost

        if (
            remaining_budget is not None
            and remaining_seconds is not None
            and remaining_seconds > 0
            and remaining_budget > 0
        ):
            budget_interval = (
                remaining_seconds / remaining_budget
            )

            interval = max(interval, budget_interval)

        interval = max(
            MIN_SCAN_INTERVAL_SECONDS,
            interval,
        )

        interval = min(
            MAX_SCAN_INTERVAL_SECONDS,
            interval,
        )

        return int(round(interval))

    def status(self, now=None):
        current = now or datetime.now()

        credit_status = get_credit_status()

        active = self.is_active(current)

        remaining_seconds = self.seconds_until_stop(current)

        remaining_budget = credit_status["remaining_planned_budget"]

        if active and remaining_budget > 0:
            scheduler_status = "ACTIVE"
        elif not active:
            scheduler_status = "PAUSED"
        else:
            scheduler_status = "BUDGET_LIMIT"

        return {
            "scanner_status": scheduler_status,
            "active": active,
            "current_time": current.isoformat(),
            "next_pair": self.scanner.peek_pair(),
            "remaining_seconds_today": remaining_seconds,
            "remaining_planned_budget": remaining_budget,
            "planned_budget": PLANNED_BUDGET,
            "safety_reserve": credit_status["safety_reserve"],
            "credits_used_today": credit_status["credits_used_today"],
            "credits_remaining": credit_status["credits_remaining"],
        }

    def next_scan(self, now=None, actual_cost=1):
        current = now or datetime.now()

        status = self.status(current)

        if not status["active"]:
            return {
                "allowed": False,
                "reason": "Scanner outside active window",
                "status": status,
            }

        if status["remaining_planned_budget"] <= 0:
            return {
                "allowed": False,
                "reason": "Planned credit budget exhausted",
                "status": status,
            }

        interval = self.calculate_interval(
            actual_cost=actual_cost,
            remaining_budget=status["remaining_planned_budget"],
            remaining_seconds=status["remaining_seconds_today"],
        )

        pair = self.scanner.next_pair()

        return {
            "allowed": True,
            "pair": pair,
            "interval_seconds": interval,
            "status": status,
        }
