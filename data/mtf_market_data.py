from config.timeframes import TRADING_MODES
from data.market_data import fetch_multi_timeframe_data


def get_mode_timeframes(mode):
    if mode not in TRADING_MODES:
        return {
            "status": "REJECTED",
            "reason": f"Unsupported trading mode: {mode}",
        }

    config = TRADING_MODES[mode]

    ordered = []
    for group in ("primary", "confirmation", "bias"):
        for timeframe in config.get(group, []):
            if timeframe not in ordered:
                ordered.append(timeframe)

    if not ordered:
        return {
            "status": "REJECTED",
            "reason": f"No timeframes configured for mode: {mode}",
        }

    return {
        "status": "VALID",
        "mode": mode,
        "timeframes": ordered,
    }


def fetch_mode_market_data(
    symbol,
    mode,
    outputsize=500,
    provider="twelvedata",
):
    timeframe_result = get_mode_timeframes(mode)

    if timeframe_result["status"] != "VALID":
        return timeframe_result

    result = fetch_multi_timeframe_data(
        symbol=symbol,
        timeframes=timeframe_result["timeframes"],
        outputsize=outputsize,
        provider=provider,
    )

    if result["status"] != "VALID":
        return result

    return {
        "status": "VALID",
        "provider": provider,
        "symbol": symbol,
        "mode": mode,
        "timeframes": result["timeframes"],
    }
