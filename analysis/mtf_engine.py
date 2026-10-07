from analysis.unified_engine import analyze_timeframe


def analyze_multi_timeframe(timeframes):
    results = {}

    for timeframe, candles in timeframes.items():
        results[timeframe] = analyze_timeframe(candles)

    return results
