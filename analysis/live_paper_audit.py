from analysis.live_paper import run_live_paper_analysis
from analysis.execution_audit import (
    query_execution_audits,
    summarize_execution_audits,
)


def run_live_paper_with_audit(
    symbol,
    mode,
    account_balance=10000,
    risk_percent=1.0,
    outputsize=500,
    audit_file=None,
):
    result = run_live_paper_analysis(
        symbol=symbol,
        mode=mode,
        account_balance=account_balance,
        risk_percent=risk_percent,
        outputsize=outputsize,
    )

    audits = query_execution_audits(
        execution_status="PAPER_ACCEPTED",
        mode="PAPER",
        limit=1,
        audit_file=audit_file,
    )

    summary = summarize_execution_audits(
        audit_file=audit_file,
    )

    return {
        "status": result["status"],
        "symbol": result.get("symbol", symbol),
        "mode": result.get("mode", mode),
        "execution": result.get("execution"),
        "analysis": result.get("analysis"),
        "audit": {
            "latest": audits,
            "summary": summary,
        },
    }
