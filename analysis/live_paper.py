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
            "symbol": symbol,
            "mode": mode,
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


def run_live_paper_session(
    symbol,
    mode,
    session,
    account_balance=10000,
    risk_percent=1.0,
    outputsize=500,
):
    if not isinstance(session, dict):
        return {
            "status": "REJECTED",
            "reason": "Invalid session",
        }

    if session.get("status") != "READY":
        return {
            "status": "REJECTED",
            "reason": "Session is not ready",
        }

    from analysis.paper_session import add_session_order

    result = run_live_paper_analysis(
        symbol=symbol,
        mode=mode,
        account_balance=account_balance,
        risk_percent=risk_percent,
        outputsize=outputsize,
    )

    execution = result.get("execution")

    if not isinstance(execution, dict):
        return {
            "status": result.get("status", "UNKNOWN"),
            "symbol": symbol,
            "mode": mode,
            "analysis": result.get("analysis"),
            "execution": None,
            "session": None,
        }

    if execution.get("status") != "PAPER_ACCEPTED":
        return {
            "status": result.get("status", execution.get("status")),
            "symbol": symbol,
            "mode": mode,
            "analysis": result.get("analysis"),
            "execution": execution,
            "session": None,
        }

    order = execution.get("order")

    if not isinstance(order, dict):
        order = execution

    session_result = add_session_order(
        session,
        order,
    )

    if session_result.get("status") != "ADDED":
        return {
            "status": "REJECTED",
            "reason": session_result.get("reason"),
            "symbol": symbol,
            "mode": mode,
            "analysis": result.get("analysis"),
            "execution": execution,
            "session": session_result,
        }

    return {
        "status": "PAPER_SESSION_ACCEPTED",
        "symbol": symbol,
        "mode": mode,
        "analysis": result.get("analysis"),
        "execution": execution,
        "session": session_result,
    }
