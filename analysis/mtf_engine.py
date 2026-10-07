from analysis.unified_engine import analyze_timeframe
from analysis.mtf_confluence import calculate_mtf_confluence


def analyze_multi_timeframe(timeframes):
    results = {}

    for timeframe, candles in timeframes.items():
        results[timeframe] = analyze_timeframe(candles)

    final_confluence = calculate_mtf_confluence(results)

    return {
        "timeframes": results,
        "confluence": final_confluence,
    }
