from analysis.mtf_engine import analyze_multi_timeframe
from data.mtf_market_data import fetch_mode_market_data


def analyze_live_market(
    symbol,
    mode,
    account_balance=None,
    risk_percent=None,
    outputsize=500,
    provider="twelvedata",
):
    market_data = fetch_mode_market_data(
        symbol=symbol,
        mode=mode,
        outputsize=outputsize,
        provider=provider,
    )

    if market_data["status"] != "VALID":
        return {
            "status": "REJECTED",
            "reason": market_data.get(
                "reason",
                "Market data fetch failed",
            ),
            "market_data": market_data,
        }

    analysis = analyze_multi_timeframe(
        timeframes=market_data["timeframes"],
        mode=mode,
        account_balance=account_balance,
        risk_percent=risk_percent,
    )

    return {
        "status": "VALID",
        "symbol": symbol,
        "mode": mode,
        "market_data": market_data,
        "analysis": analysis,
    }
