from analysis.live_mtf import analyze_live_market
from analysis.execution_gateway import execute_order


def run_live_paper_analysis(
    symbol,
    mode,
    account_balance=10000,
    risk_percent=1.0,
    outputsize=500,
):
    analysis_result = analyze_live_market(
        symbol=symbol,
        mode=mode,
        account_balance=account_balance,
        risk_percent=risk_percent,
        outputsize=outputsize,
    )

    if analysis_result["status"] != "VALID":
        return {
            "status": "REJECTED",
            "reason": analysis_result.get("reason"),
            "analysis": analysis_result,
            "execution": None,
        }

    analysis = analysis_result["analysis"]
    paper_order = analysis.get("paper_order")

    if not paper_order:
        return {
            "status": "NO_TRADE",
            "reason": "No paper order generated",
            "analysis": analysis_result,
            "execution": None,
        }

    execution = execute_order(
        order=paper_order,
        mode="PAPER",
    )

    return {
        "status": execution.get("status", "UNKNOWN"),
        "symbol": symbol,
        "mode": mode,
        "analysis": analysis_result,
        "execution": execution,
    }
