from data.market_data import fetch_market_data
from data.scanner.credit_tracker import (
    can_spend,
    get_credit_status,
    reconcile_credits,
    record_request,
    reserve_credits,
)
from data.scanner.market_cache import market_cache


def _extract_int(headers, names):
    if not isinstance(headers, dict):
        return None

    for name in names:
        value = headers.get(name)

        if value is None:
            continue

        try:
            return int(str(value).strip())
        except (TypeError, ValueError):
            continue

    return None


def estimate_request_cost(result=None):
    """
    Conservative default request estimate.

    Provider-specific accounting is reconciled separately.
    We do not assume that a 'credits-left' header is a per-request cost.
    """
    return 1


def infer_actual_credit_cost(
    result,
    before_used=None,
    before_remaining=None,
):
    """
    Determine actual request cost only when provider metadata supports it.

    Supported signals:
    1. Explicit per-request credit-consumed fields.
    2. Cumulative credits-used delta.
    3. Credits-left delta, when a previous remaining value is known.

    Otherwise return None so callers can use the conservative estimate.
    """
    if not isinstance(result, dict):
        return None

    headers = result.get("credit_headers") or {}

    explicit = _extract_int(
        headers,
        (
            "credits-consumed",
            "credit-consumed",
            "api-credits-consumed",
            "x-credits-consumed",
        ),
    )

    if explicit is not None and explicit >= 0:
        return explicit

    used_after = _extract_int(
        headers,
        (
            "api-credits-used",
            "credits-used",
            "x-credits-used",
        ),
    )

    if (
        used_after is not None
        and before_used is not None
        and used_after >= before_used
    ):
        return used_after - before_used

    remaining_after = _extract_int(
        headers,
        (
            "api-credits-left",
            "credits-left",
            "x-credits-left",
            "api-credits-remaining",
            "credits-remaining",
        ),
    )

    if (
        remaining_after is not None
        and before_remaining is not None
        and before_remaining >= remaining_after
    ):
        return before_remaining - remaining_after

    return None


def get_market_data(
    symbol,
    timeframe,
    outputsize=500,
    provider="twelvedata",
    force_refresh=False,
    critical=False,
):
    if not force_refresh:
        cached = market_cache.get(symbol, timeframe)

        if cached["status"] == "HIT":
            record_request(
                credits_consumed=0,
                symbol=symbol,
                timeframe=timeframe,
                request_type="cache",
                success=True,
                cache_hit=True,
                reason="Fresh market data available in cache",
            )

            return {
                "status": "VALID",
                "source": "cache",
                "symbol": symbol,
                "timeframe": timeframe,
                "candles": cached["candles"],
                "meta": cached.get("meta", {}),
                "cache": cached,
                "credit_status": get_credit_status(),
            }

    expected_cost = estimate_request_cost()

    reservation = reserve_credits(
        expected_credits=expected_cost,
        critical=critical,
    )

    if not reservation["reserved"]:
        return {
            "status": "REJECTED",
            "reason": "Credit budget protection active",
            "credit_status": reservation["credit_status"],
        }

    before_status = reservation["credit_status"]

    before_used = before_status.get("credits_used_today")
    before_remaining = before_status.get("credits_remaining")

    result = fetch_market_data(
        symbol=symbol,
        timeframe=timeframe,
        outputsize=outputsize,
        provider=provider,
    )

    provider_headers = (
        result.get("credit_headers", {})
        if isinstance(result, dict)
        else {}
    )

    actual_cost = infer_actual_credit_cost(
        result,
        before_used=before_used,
        before_remaining=before_remaining,
    )

    if actual_cost is None:
        actual_cost = expected_cost

    actual_cost = max(0, int(actual_cost))

    if result.get("status") != "VALID":
        credit_status = reconcile_credits(
            reserved_credits=expected_cost,
            actual_credits=actual_cost,
            symbol=symbol,
            timeframe=timeframe,
            success=False,
            reason=result.get("reason", "Market data request failed"),
            provider_headers=provider_headers,
        )

        result["credit_status"] = credit_status
        result["credits_consumed"] = actual_cost
        return result

    candles = result.get("candles")

    if not isinstance(candles, list) or not candles:
        credit_status = reconcile_credits(
            reserved_credits=expected_cost,
            actual_credits=actual_cost,
            symbol=symbol,
            timeframe=timeframe,
            success=False,
            reason="Provider returned no candles",
            provider_headers=provider_headers,
        )

        return {
            "status": "REJECTED",
            "reason": "Provider returned no candles",
            "credit_status": credit_status,
            "credits_consumed": actual_cost,
        }

    market_cache.put(
        symbol=symbol,
        timeframe=timeframe,
        candles=candles,
        meta=result.get("meta", {}),
    )

    credit_status = reconcile_credits(
        reserved_credits=expected_cost,
        actual_credits=actual_cost,
        symbol=symbol,
        timeframe=timeframe,
        success=True,
        cache_hit=False,
        reason="Fresh TwelveData request",
        provider_headers=provider_headers,
    )

    return {
        "status": "VALID",
        "source": "twelvedata",
        "symbol": symbol,
        "timeframe": timeframe,
        "candles": candles,
        "meta": result.get("meta", {}),
        "provider_headers": result.get("provider_headers", {}),
        "credit_headers": provider_headers,
        "credits_consumed": actual_cost,
        "credit_status": credit_status,
    }
