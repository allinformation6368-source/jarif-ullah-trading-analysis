from datetime import datetime, timedelta, timezone


def _now_utc():
    return datetime.now(timezone.utc)


def _parse_time(value):
    if isinstance(value, datetime):
        dt = value
    elif isinstance(value, str):
        try:
            dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
    else:
        return None

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    return dt


class SetupPersistence:
    """
    Strategy-agnostic setup persistence.

    Stores a setup after a strategy identifies it. The scanner can then
    recognize that the same setup is still active across subsequent scans,
    helping prevent missed entries without generating BUY/SELL decisions.
    """

    def __init__(self, default_ttl_seconds=300):
        self.default_ttl_seconds = int(default_ttl_seconds)
        self._setups = {}

    @staticmethod
    def _key(pair, mode, setup_id):
        return f"{pair}|{mode}|{setup_id}"

    def observe(
        self,
        pair,
        mode,
        setup_id,
        candle_id,
        metadata=None,
        ttl_seconds=None,
        now=None,
    ):
        if not pair:
            raise ValueError("pair is required")
        if not mode:
            raise ValueError("mode is required")
        if not setup_id:
            raise ValueError("setup_id is required")
        if not candle_id:
            raise ValueError("candle_id is required")

        now = _parse_time(now) if now is not None else _now_utc()
        if now is None:
            raise ValueError("invalid now")

        ttl = int(
            self.default_ttl_seconds
            if ttl_seconds is None
            else ttl_seconds
        )

        if ttl <= 0:
            raise ValueError("ttl_seconds must be positive")

        key = self._key(pair, mode, setup_id)
        existing = self._setups.get(key)

        if existing and existing["expires_at"] > now:
            existing["last_seen_at"] = now
            existing["last_candle_id"] = candle_id
            existing["observations"] += 1

            if metadata:
                existing["metadata"].update(metadata)

            return {
                **existing,
                "key": key,
                "state": "PERSISTING",
            }

        record = {
            "pair": pair,
            "mode": mode,
            "setup_id": setup_id,
            "first_seen_at": now,
            "last_seen_at": now,
            "last_candle_id": candle_id,
            "expires_at": now + timedelta(seconds=ttl),
            "observations": 1,
            "metadata": dict(metadata or {}),
        }

        self._setups[key] = record

        return {
            **record,
            "key": key,
            "state": "NEW",
        }

    def get(
        self,
        pair,
        mode,
        setup_id,
        now=None,
    ):
        now = _parse_time(now) if now is not None else _now_utc()
        if now is None:
            raise ValueError("invalid now")

        key = self._key(pair, mode, setup_id)
        record = self._setups.get(key)

        if record is None:
            return None

        if record["expires_at"] <= now:
            self._setups.pop(key, None)
            return None

        return {
            **record,
            "key": key,
            "state": "ACTIVE",
        }

    def invalidate(self, pair, mode, setup_id):
        key = self._key(pair, mode, setup_id)
        return self._setups.pop(key, None) is not None

    def clear(self):
        self._setups.clear()

    def snapshot(self, now=None):
        now = _parse_time(now) if now is not None else _now_utc()
        if now is None:
            raise ValueError("invalid now")

        active = {}

        for key in list(self._setups):
            record = self.get(
                record_pair := self._setups[key]["pair"],
                self._setups[key]["mode"],
                self._setups[key]["setup_id"],
                now=now,
            )
            if record:
                active[key] = record

        return active
