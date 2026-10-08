from data.twelve_data import fetch_twelve_data_candles


def fetch_market_data(
    symbol,
    timeframe,
    outputsize=500,
    provider="twelvedata",
):
    if provider != "twelvedata":
        return {
            "status": "REJECTED",
            "reason": f"Unsupported data provider: {provider}",
        }

    result = fetch_twelve_data_candles(
        symbol=symbol,
        interval=timeframe,
        outputsize=outputsize,
    )

    if result["status"] != "VALID":
        return result

    return {
        "status": "VALID",
        "provider": provider,
        "symbol": symbol,
        "timeframe": timeframe,
        "candles": result["candles"],
        "meta": result.get("meta", {}),
    }


def fetch_multi_timeframe_data(
    symbol,
    timeframes,
    outputsize=500,
    provider="twelvedata",
):
    if not isinstance(timeframes, (list, tuple)):
        return {
            "status": "REJECTED",
            "reason": "Timeframes must be a list or tuple",
        }

    results = {}

    for timeframe in timeframes:
        result = fetch_market_data(
            symbol=symbol,
            timeframe=timeframe,
            outputsize=outputsize,
            provider=provider,
        )

        if result["status"] != "VALID":
            return {
                "status": "REJECTED",
                "reason": f"Failed timeframe {timeframe}: "
                f"{result.get('reason', 'Unknown error')}",
            }

        results[timeframe] = result["candles"]

    return {
        "status": "VALID",
        "provider": provider,
        "symbol": symbol,
        "timeframes": results,
    }
