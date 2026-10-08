from analysis.paper_session import (
    build_session_audit_summary,
    get_session_snapshot,
)


def generate_paper_report(session, audits):
    if not isinstance(session, dict):
        return {
            "status": "REJECTED",
            "reason": "Invalid session",
        }

    if not isinstance(audits, list):
        return {
            "status": "REJECTED",
            "reason": "Invalid audits",
        }

    snapshot = get_session_snapshot(session)

    if snapshot["status"] != "VALID":
        return snapshot

    audit_summary = build_session_audit_summary(
        session,
        audits,
    )

    if audit_summary["status"] != "VALID":
        return audit_summary

    performance = snapshot["performance"]

    return {
        "status": "VALID",
        "symbol": session.get("symbol"),
        "mode": session.get("mode"),
        "session_status": session.get("status"),
        "orders": snapshot["orders"],
        "open_trades": snapshot["open_trades"],
        "closed_trades": performance["total_trades"],
        "execution": {
            "audit_count": audit_summary["audit_count"],
            "accepted": audit_summary["accepted_audits"],
            "rejected": audit_summary["rejected_audits"],
        },
        "performance": {
            "starting_equity": performance["starting_equity"],
            "ending_equity": performance["ending_equity"],
            "net_pnl": performance["net_pnl"],
            "win_rate": performance["win_rate"],
            "profit_factor": performance["profit_factor"],
            "max_drawdown": performance["max_drawdown"],
            "average_pnl": performance["average_pnl"],
            "average_r": performance["average_r"],
        },
    }
