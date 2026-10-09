import json
import os
from datetime import date, datetime, timezone
from threading import RLock

DAILY_LIMIT = 800
SAFETY_RESERVE = 50
PLANNED_BUDGET = DAILY_LIMIT - SAFETY_RESERVE

STATE_DIR = os.path.join(".runtime", "scanner")
STATE_FILE = os.path.join(STATE_DIR, "credit_state.json")

_lock = RLock()


def _today():
    return date.today().isoformat()


def _default_state():
    return {
        "date": _today(),
        "credits_used_today": 0,
        "reserved_credits_today": 0,
        "requests_today": 0,
        "last_request_at": None,
        "events": [],
    }


def _load():
    os.makedirs(STATE_DIR, exist_ok=True)

    if not os.path.exists(STATE_FILE):
        return _default_state()

    try:
        with open(STATE_FILE, "r", encoding="utf-8") as handle:
            state = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return _default_state()

    if state.get("date") != _today():
        return _default_state()

    state.setdefault("credits_used_today", 0)
    state.setdefault("reserved_credits_today", 0)
    state.setdefault("requests_today", 0)
    state.setdefault("last_request_at", None)
    state.setdefault("events", [])

    return state


def _save(state):
    os.makedirs(STATE_DIR, exist_ok=True)

    temporary = f"{STATE_FILE}.tmp"

    with open(temporary, "w", encoding="utf-8") as handle:
        json.dump(state, handle, indent=2)

    os.replace(temporary, STATE_FILE)


def get_credit_status():
    with _lock:
        state = _load()

        used = max(0, int(state.get("credits_used_today", 0)))
        reserved = max(0, int(state.get("reserved_credits_today", 0)))

        available_planned = max(
            0,
            PLANNED_BUDGET - used - reserved,
        )

        remaining_total = max(
            0,
            DAILY_LIMIT - used - reserved,
        )

        if used + reserved >= PLANNED_BUDGET:
            scanner_status = "BUDGET_LIMIT"
        else:
            scanner_status = "ACTIVE"

        return {
            "daily_limit": DAILY_LIMIT,
            "planned_budget": PLANNED_BUDGET,
            "safety_reserve": SAFETY_RESERVE,
            "credits_used_today": used,
            "credits_remaining": remaining_total,
            "reserved_credits_today": reserved,
            "remaining_planned_budget": available_planned,
            "requests_today": int(state.get("requests_today", 0)),
            "scanner_status": scanner_status,
            "date": state["date"],
        }


def can_spend(expected_credits=1, critical=False):
    if not isinstance(expected_credits, int) or expected_credits <= 0:
        return False

    with _lock:
        state = _load()

        used = max(0, int(state.get("credits_used_today", 0)))
        reserved = max(0, int(state.get("reserved_credits_today", 0)))

        limit = DAILY_LIMIT if critical else PLANNED_BUDGET

        return used + reserved + expected_credits <= limit


def reserve_credits(expected_credits=1, critical=False):
    if not isinstance(expected_credits, int) or expected_credits <= 0:
        return {
            "reserved": False,
            "reason": "Invalid expected credit amount",
            "credit_status": get_credit_status(),
        }

    with _lock:
        state = _load()

        used = max(0, int(state.get("credits_used_today", 0)))
        reserved = max(0, int(state.get("reserved_credits_today", 0)))

        limit = DAILY_LIMIT if critical else PLANNED_BUDGET

        if used + reserved + expected_credits > limit:
            return {
                "reserved": False,
                "reason": "Credit budget protection active",
                "credit_status": get_credit_status(),
            }

        state["reserved_credits_today"] = reserved + expected_credits
        _save(state)

        return {
            "reserved": True,
            "reserved_credits": expected_credits,
            "credit_status": get_credit_status(),
        }


def reconcile_credits(
    reserved_credits,
    actual_credits,
    symbol=None,
    timeframe=None,
    request_type="time_series",
    success=False,
    cache_hit=False,
    reason=None,
    provider_headers=None,
):
    if not isinstance(reserved_credits, int) or reserved_credits < 0:
        raise ValueError("reserved_credits must be a non-negative integer")

    if not isinstance(actual_credits, int) or actual_credits < 0:
        raise ValueError("actual_credits must be a non-negative integer")

    with _lock:
        state = _load()

        current_reserved = max(
            0,
            int(state.get("reserved_credits_today", 0)),
        )

        state["reserved_credits_today"] = max(
            0,
            current_reserved - reserved_credits,
        )

        state["credits_used_today"] += actual_credits
        state["requests_today"] += 1

        timestamp = datetime.now(timezone.utc).isoformat()
        state["last_request_at"] = timestamp

        state["events"].append(
            {
                "timestamp": timestamp,
                "symbol": symbol,
                "timeframe": timeframe,
                "request_type": request_type,
                "success": bool(success),
                "cache_hit": bool(cache_hit),
                "reserved_credits": reserved_credits,
                "credits_consumed": actual_credits,
                "reason": reason,
                "provider_headers": provider_headers or {},
            }
        )

        state["events"] = state["events"][-500:]

        _save(state)

        return get_credit_status()


def record_request(
    credits_consumed,
    symbol=None,
    timeframe=None,
    request_type="time_series",
    success=False,
    cache_hit=False,
    reason=None,
    provider_headers=None,
):
    if not isinstance(credits_consumed, int) or credits_consumed < 0:
        raise ValueError(
            "credits_consumed must be a non-negative integer"
        )

    return reconcile_credits(
        reserved_credits=0,
        actual_credits=credits_consumed,
        symbol=symbol,
        timeframe=timeframe,
        request_type=request_type,
        success=success,
        cache_hit=cache_hit,
        reason=reason,
        provider_headers=provider_headers,
    )
