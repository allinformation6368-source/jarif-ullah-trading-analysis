from analysis.paper_session import (
    add_session_order,
    build_session_audit_summary,
    create_paper_session,
    update_session_orders,
)


def test_session_audit_summary_tracks_accepted_and_closed_trade():
    session = create_paper_session(
        symbol="BTC/USD",
        mode="scalping",
        starting_balance=10000,
    )

    add_session_order(
        session,
        {
            "status": "OPEN",
            "signal": "BUY",
            "entry": 100.0,
            "stop_loss": 95.0,
            "take_profit": 110.0,
            "pnl": 0,
        },
    )

    audits = [
        {
            "status": "PAPER_ACCEPTED",
            "mode": "PAPER",
        }
    ]

    update_session_orders(
        session,
        [
            {
                "high": 112.0,
                "low": 99.0,
            }
        ],
    )

    result = build_session_audit_summary(
        session,
        audits,
    )

    assert result["status"] == "VALID"
    assert result["audit_count"] == 1
    assert result["accepted_audits"] == 1
    assert result["rejected_audits"] == 0
    assert result["session_orders"] == 1
    assert result["open_orders"] == 0
    assert result["closed_orders"] == 1
    assert result["performance"]["net_pnl"] == 10.0


def test_session_audit_summary_tracks_rejections():
    session = create_paper_session(
        starting_balance=10000,
    )

    audits = [
        {
            "status": "PAPER_ACCEPTED",
            "mode": "PAPER",
        },
        {
            "status": "REJECTED",
            "mode": "PAPER",
            "reason": "Invalid signal",
        },
        {
            "status": "REJECTED",
            "mode": "PAPER",
            "reason": "Risk rejected",
        },
    ]

    result = build_session_audit_summary(
        session,
        audits,
    )

    assert result["status"] == "VALID"
    assert result["audit_count"] == 3
    assert result["accepted_audits"] == 1
    assert result["rejected_audits"] == 2
    assert result["session_orders"] == 0
    assert result["closed_orders"] == 0
    assert result["performance"]["total_trades"] == 0


def test_session_audit_summary_rejects_invalid_audits():
    session = create_paper_session()

    result = build_session_audit_summary(
        session,
        None,
    )

    assert result["status"] == "REJECTED"


def test_session_audit_summary_rejects_invalid_session():
    result = build_session_audit_summary(
        None,
        [],
    )

    assert result["status"] == "REJECTED"


def test_session_audit_summary_counts_multiple_orders():
    session = create_paper_session(
        starting_balance=10000,
    )

    add_session_order(
        session,
        {
            "status": "CLOSED",
            "signal": "BUY",
            "pnl": 20.0,
            "risk_amount": 10.0,
        },
    )

    add_session_order(
        session,
        {
            "status": "OPEN",
            "signal": "SELL",
            "entry": 100.0,
            "stop_loss": 105.0,
            "take_profit": 90.0,
            "pnl": 0,
        },
    )

    audits = [
        {
            "status": "PAPER_ACCEPTED",
            "mode": "PAPER",
        },
        {
            "status": "PAPER_ACCEPTED",
            "mode": "PAPER",
        },
    ]

    result = build_session_audit_summary(
        session,
        audits,
    )

    assert result["status"] == "VALID"
    assert result["accepted_audits"] == 2
    assert result["session_orders"] == 2
    assert result["closed_orders"] == 1
    assert result["open_orders"] == 1
    assert result["performance"]["net_pnl"] == 20.0
    assert result["performance"]["open_trades"] == 1
