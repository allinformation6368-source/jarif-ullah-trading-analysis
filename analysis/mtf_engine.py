from analysis.unified_engine import analyze_timeframe
from analysis.mtf_confluence import calculate_mtf_confluence
from analysis.trade_decision import evaluate_trade_decision
from analysis.entry_quality import evaluate_entry_quality
from analysis.risk_management import calculate_smc_risk_from_candles
from analysis.position_sizing import calculate_position_size
from analysis.risk_guard import validate_trade_risk
from config.timeframes import TRADING_MODES


def _get_execution_timeframe(timeframes, mode=None):
    if mode in TRADING_MODES:
        primary = TRADING_MODES[mode]["primary"]

        for timeframe in reversed(primary):
            if timeframe in timeframes:
                return timeframe

    if timeframes:
        return next(reversed(timeframes))

    return None


def analyze_multi_timeframe(
    timeframes,
    mode=None,
    account_balance=None,
    risk_percent=None,
):
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

    risk = None
    position_sizing = None
    risk_guard = None

    if decision["decision"] == "ENTRY_READY":
        execution_timeframe = _get_execution_timeframe(
            timeframes,
            mode=mode,
        )

        if execution_timeframe is not None:
            risk = calculate_smc_risk_from_candles(
                signal=decision["signal"],
                candles=timeframes[execution_timeframe],
                analysis=results[execution_timeframe],
                risk_reward=2,
            )

            if (
                risk["status"] == "VALID"
                and account_balance is not None
                and risk_percent is not None
            ):
                position_sizing = calculate_position_size(
                    account_balance=account_balance,
                    risk_percent=risk_percent,
                    entry=risk["entry"],
                    stop_loss=risk["stop_loss"],
                )

            risk_guard = validate_trade_risk(
                risk=risk,
                position_sizing=position_sizing,
            )

    return {
        "timeframes": results,
        "confluence": final_confluence,
        "decision": decision,
        "entry_quality": entry_quality,
        "risk": risk,
        "position_sizing": position_sizing,
        "risk_guard": risk_guard,
    }
