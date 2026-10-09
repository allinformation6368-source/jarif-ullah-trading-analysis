from datetime import datetime

from data.scanner.scheduler import ScannerScheduler
from data.scanner.market_data_layer import get_market_data
from data.scanner.scanner_config import SCANNER_PAIRS
from data.scanner.candle_guard import CandleGuard
from data.scanner.setup_persistence import SetupPersistence
from data.scanner.timeframe_policy import (
    required_timeframes,
    screening_timeframes,
    deeper_timeframes,
)


class ScannerEngine:
    """
    Controlled scanner orchestration.

    Flow:
        scheduler
          -> one pair
          -> cheap primary-TF screening
          -> deeper confirmation/bias only if screening passes

    All market data access goes through the central market-data layer.
    """

    def __init__(self, scheduler=None):
        self.scheduler = scheduler or ScannerScheduler()
        self.scans_completed = 0
        self.last_result = None
        self.candle_guard = CandleGuard()
        self.setup_persistence = SetupPersistence()

    @staticmethod
    def _fetch_timeframes(pair, timeframes, outputsize=100):
        data = {}

        for timeframe in timeframes:
            data[timeframe] = get_market_data(
                symbol=pair,
                timeframe=timeframe,
                outputsize=outputsize,
                provider="twelvedata",
            )

        return data

    @staticmethod
    def _screen_passes(screening_data):
        """
        Conservative structural gate.

        A real strategy/indicator layer can replace this later.
        For now, only valid candle data may pass.
        """
        if not screening_data:
            return False

        for result in screening_data.values():
            candles = result.get("candles") or []
            if not candles:
                return False

        return True

    def next_scan(
        self,
        mode="scalping",
        outputsize=100,
        now=None,
        force_deep=False,
        timeframe=None,
    ):
        decision = self.scheduler.next_scan(now=now, actual_cost=1)

        if not decision["allowed"]:
            result = {
                "status": "SKIPPED",
                "reason": decision["reason"],
                "scheduler": decision["status"],
            }
            self.last_result = result
            return result

        pair = decision["pair"]

        primary_tfs = screening_timeframes(mode)
        deeper_tfs = deeper_timeframes(mode)
        required_tfs = required_timeframes(mode)

        screening_data = self._fetch_timeframes(
            pair,
            primary_tfs,
            outputsize=outputsize,
        )

        freshness = {}
        fresh_screening_data = {}

        for timeframe, data in screening_data.items():
            candles = data.get("candles") or []

            guard = self.candle_guard.check(
                pair,
                timeframe,
                candles,
            )

            freshness[timeframe] = guard

            if guard["process"]:
                fresh_screening_data[timeframe] = data

        # Screening validity is independent of candle freshness.
        # Empty/invalid primary data must fail screening, while duplicate
        # candles must only block repeated processing.
        screening_passed = self._screen_passes(screening_data)

        screening_fresh = bool(screening_data) and all(
            freshness.get(timeframe, {}).get("process") is True
            for timeframe in primary_tfs
        )

        deep_data = {}
        fresh_deep_data = {}

        # Do not spend deeper-analysis credits on duplicate/stale primary
        # candles. force_deep is the explicit override.
        if (screening_passed and screening_fresh) or force_deep:
            deep_data = self._fetch_timeframes(
                pair,
                deeper_tfs,
                outputsize=outputsize,
            )

            for timeframe, data in deep_data.items():
                candles = data.get("candles") or []

                guard = self.candle_guard.check(
                    pair,
                    timeframe,
                    candles,
                )

                freshness[timeframe] = guard

                if guard["process"]:
                    fresh_deep_data[timeframe] = data

        for timeframe, data in {
            **fresh_screening_data,
            **fresh_deep_data,
        }.items():
            self.candle_guard.mark_processed(
                pair,
                timeframe,
                data.get("candles") or [],
            )

        self.scans_completed += 1

        all_data = {}
        all_data.update(screening_data)
        all_data.update(deep_data)

        credits_consumed = sum(
            int(result.get("credits_consumed", 0) or 0)
            for result in all_data.values()
        )

        # Backward-compatible top-level fields for the Step 5 scanner contract.
        first_data = next(iter(all_data.values()), {})
        source = first_data.get("source")
        if source is None:
            source = "unknown"

        result = {
            "status": "SCANNED",
            "pair": pair,
            "mode": mode,
            "source": source,
            "required_timeframes": required_tfs,
            "screening_timeframes": primary_tfs,
            "deeper_timeframes": deeper_tfs,
            "screening_passed": screening_passed,
            "screening_fresh": screening_fresh,
            "deep_analysis_run": bool(deep_data),
            "fresh_candles": {
                timeframe: info
                for timeframe, info in freshness.items()
                if info.get("process")
            },
            "duplicate_or_stale": {
                timeframe: info
                for timeframe, info in freshness.items()
                if not info.get("process")
            },
            "data": all_data,
            "credits_consumed": credits_consumed,
            "interval_seconds": decision["interval_seconds"],
            "scans_completed": self.scans_completed,
            "timestamp": datetime.now().isoformat(),
        }

        # Setup persistence is intentionally strategy-agnostic.
        # A future strategy layer may provide setup candidates through
        # `result["setup_candidates"]`; the engine only tracks their lifecycle.
        setup_candidates = result.get("setup_candidates") or []
        persisted_setups = []

        for setup in setup_candidates:
            if not isinstance(setup, dict):
                continue

            setup_id = setup.get("setup_id")
            candle_id = setup.get("candle_id")

            if not setup_id or not candle_id:
                continue

            persisted = self.setup_persistence.observe(
                pair=pair,
                mode=mode,
                setup_id=setup_id,
                candle_id=candle_id,
                metadata=setup.get("metadata"),
                ttl_seconds=setup.get("ttl_seconds"),
                now=result["timestamp"],
            )

            persisted_setups.append(persisted)

        result["persisted_setups"] = persisted_setups

        self.last_result = result
        return result

    def status(self):
        return {
            "pairs": list(SCANNER_PAIRS),
            "scans_completed": self.scans_completed,
            "last_result": self.last_result,
            "active_setups": self.setup_persistence.snapshot(),
            "scheduler": self.scheduler.status(),
        }
