from analysis.unified_engine import analyze_timeframe
from analysis.mtf_confluence import calculate_mtf_confluence
from analysis.trade_decision import evaluate_trade_decision


def analyze_multi_timeframe(timeframes, mode=None):
    results = {}

    for timeframe, candles in timeframes.items():
        results[timeframe] = analyze_timeframe(candles)

    final_confluence = calculate_mtf_confluence(
        results,
        mode=mode,
    )

    decision = evaluate_trade_decision(
        final_confluence
    )

    return {
        "timeframes": results,
        "confluence": final_confluence,
        "decision": decision,
    }
