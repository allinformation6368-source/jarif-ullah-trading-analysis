import threading
from datetime import datetime, timezone


DEFAULT_TTL_SECONDS = {
    "1min": 60,
    "5min": 300,
    "15min": 900,
    "30min": 1800,
    "1h": 3600,
    "2h": 7200,
    "4h": 14400,
    "1day": 86400,
    "1week": 604800,
}


class MarketDataCache:
    def __init__(self, ttl_seconds=None):
        self._data = {}
        self._lock = threading.RLock()
        self._ttl_seconds = dict(DEFAULT_TTL_SECONDS)

        if ttl_seconds:
            self._ttl_seconds.update(ttl_seconds)

    def _key(self, symbol, timeframe):
        return (
            str(symbol).strip().upper(),
            str(timeframe).strip(),
        )

    def _now(self):
        return datetime.now(timezone.utc)

    def get(self, symbol, timeframe):
        key = self._key(symbol, timeframe)

        with self._lock:
            item = self._data.get(key)

            if item is None:
                return {
                    "status": "MISS",
                    "reason": "No cached market data",
                }

            age = (
                self._now() - item["cached_at"]
            ).total_seconds()

            ttl = self._ttl_seconds.get(
                timeframe,
                300,
            )

            if age > ttl:
                return {
                    "status": "STALE",
                    "reason": "Cached market data expired",
                    "age_seconds": age,
                    "ttl_seconds": ttl,
                }

            return {
                "status": "HIT",
                "symbol": symbol,
                "timeframe": timeframe,
                "candles": item["candles"],
                "cached_at": item["cached_at"].isoformat(),
                "age_seconds": age,
                "ttl_seconds": ttl,
                "meta": item.get("meta", {}),
            }

    def put(
        self,
        symbol,
        timeframe,
        candles,
        meta=None,
    ):
        if not isinstance(candles, list) or not candles:
            raise ValueError("candles must be a non-empty list")

        key = self._key(symbol, timeframe)

        with self._lock:
            now = self._now()

            self._data[key] = {
                "symbol": symbol,
                "timeframe": timeframe,
                "candles": candles,
                "cached_at": now,
                "meta": meta or {},
            }

        return {
            "status": "STORED",
            "symbol": symbol,
            "timeframe": timeframe,
            "cached_at": now.isoformat(),
        }

    def invalidate(self, symbol=None, timeframe=None):
        with self._lock:
            if symbol is None and timeframe is None:
                self._data.clear()
                return

            key = self._key(symbol, timeframe)
            self._data.pop(key, None)

    def clear(self):
        self.invalidate()

    def stats(self):
        with self._lock:
            return {
                "entries": len(self._data),
                "keys": [
                    {
                        "symbol": item["symbol"],
                        "timeframe": item["timeframe"],
                        "cached_at": item["cached_at"].isoformat(),
                    }
                    for item in self._data.values()
                ],
            }


market_cache = MarketDataCache()
