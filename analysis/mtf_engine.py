from analysis.unified_engine import analyze_timeframe
from analysis.mtf_confluence import calculate_mtf_confluence
from analysis.trade_decision import evaluate_trade_decision
from analysis.entry_quality import evaluate_entry_quality


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

    entry_quality = evaluate_entry_quality(
        final_confluence,
        decision,
    )

    return {
        "timeframes": results,
        "confluence": final_confluence,
        "decision": decision,
        "entry_quality": entry_quality,
    }
