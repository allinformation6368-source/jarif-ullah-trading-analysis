from __future__ import annotations


VALID_DECISIONS = {"BUY", "SELL", "WAIT", "INVALIDATED"}


def _direction(value):
    if value in {"BUY", "BULLISH"}:
        return "BULLISH"
    if value in {"SELL", "BEARISH"}:
        return "BEARISH"
    return "NEUTRAL"


def _extract_decision(result):
    if not isinstance(result, dict):
        return "WAIT"

    decision = result.get("decision")
    if decision in VALID_DECISIONS:
        return decision

    return "WAIT"


def _tf_direction(result):
    if not isinstance(result, dict):
        return "NEUTRAL"

    decision = _extract_decision(result)

    if decision == "BUY":
        return "BULLISH"
    if decision == "SELL":
        return "BEARISH"
    if decision == "INVALIDATED":
        return "INVALIDATED"

    structure = result.get("structure")
    if isinstance(structure, dict):
        direction = _direction(structure.get("structure"))
        if direction != "NEUTRAL":
            return direction

    indicators = result.get("indicators")
    if isinstance(indicators, dict):
        direction = _direction(indicators.get("trend"))
        if direction != "NEUTRAL":
            return direction

    return "NEUTRAL"


def _fresh(result):
    if not isinstance(result, dict):
        return False

    if "fresh" in result:
        return bool(result["fresh"])

    if "is_fresh" in result:
        return bool(result["is_fresh"])

    return True


def _valid(result):
    if not isinstance(result, dict):
        return False

    if result.get("valid") is False:
        return False

    if result.get("status") in {"INVALID", "ERROR", "FAILED"}:
        return False

    return True


def validate_signal(
    timeframe_results,
    *,
    required_timeframes=None,
):
    """
    Validate a multi-timeframe signal.

    timeframe_results:
        {
            "5min": {...},
            "15min": {...},
            "1h": {...},
        }

    Returns analysis only. No execution/order/position logic.
    """

    if not isinstance(timeframe_results, dict):
        raise TypeError("timeframe_results must be a dict")

    required = list(required_timeframes or timeframe_results.keys())

    missing = [
        timeframe
        for timeframe in required
        if timeframe not in timeframe_results
    ]

    if missing:
        return {
            "decision": "WAIT",
            "valid": False,
            "reason": "MISSING_TIMEFRAME",
            "missing_timeframes": missing,
            "aligned": False,
            "contradiction": False,
            "directions": {},
        }

    invalid = [
        timeframe
        for timeframe in required
        if not _valid(timeframe_results[timeframe])
    ]

    if invalid:
        return {
            "decision": "WAIT",
            "valid": False,
            "reason": "INVALID_DATA",
            "invalid_timeframes": invalid,
            "aligned": False,
            "contradiction": False,
            "directions": {},
        }

    stale = [
        timeframe
        for timeframe in required
        if not _fresh(timeframe_results[timeframe])
    ]

    if stale:
        return {
            "decision": "WAIT",
            "valid": False,
            "reason": "STALE_DATA",
            "stale_timeframes": stale,
            "aligned": False,
            "contradiction": False,
            "directions": {},
        }

    directions = {
        timeframe: _tf_direction(timeframe_results[timeframe])
        for timeframe in required
    }

    bullish = [
        timeframe
        for timeframe, direction in directions.items()
        if direction == "BULLISH"
    ]

    bearish = [
        timeframe
        for timeframe, direction in directions.items()
        if direction == "BEARISH"
    ]

    contradiction = bool(bullish and bearish)

    if contradiction:
        return {
            "decision": "INVALIDATED",
            "valid": True,
            "reason": "MTF_CONTRADICTION",
            "missing_timeframes": [],
            "stale_timeframes": [],
            "invalid_timeframes": [],
            "directions": directions,
            "bullish_timeframes": bullish,
            "bearish_timeframes": bearish,
            "aligned": False,
            "contradiction": True,
        }

    active_directions = {
        direction
        for direction in directions.values()
        if direction in {"BULLISH", "BEARISH"}
    }

    if len(active_directions) == 1 and len(active_directions) > 0:
        direction = next(iter(active_directions))

        if direction == "BULLISH":
            decision = "BUY"
        else:
            decision = "SELL"

        return {
            "decision": decision,
            "valid": True,
            "reason": "MTF_ALIGNED",
            "missing_timeframes": [],
            "stale_timeframes": [],
            "invalid_timeframes": [],
            "directions": directions,
            "bullish_timeframes": bullish,
            "bearish_timeframes": bearish,
            "aligned": True,
            "contradiction": False,
        }

    return {
        "decision": "WAIT",
        "valid": True,
        "reason": "INSUFFICIENT_ALIGNMENT",
        "missing_timeframes": [],
        "stale_timeframes": [],
        "invalid_timeframes": [],
        "directions": directions,
        "bullish_timeframes": bullish,
        "bearish_timeframes": bearish,
        "aligned": False,
        "contradiction": False,
    }
