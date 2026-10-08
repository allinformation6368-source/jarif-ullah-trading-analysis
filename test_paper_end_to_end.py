def test_end_to_end_live_paper_session_lifecycle(monkeypatch):
    import analysis.live_paper as live_paper

    from analysis.paper_session import (
        create_paper_session,
        get_session_snapshot,
        update_session_orders,
    )

    session = create_paper_session(
        symbol="BTC/USD",
        mode="scalping",
        starting_balance=10000,
        timestamp="2026-01-01T00:00:00+00:00",
    )

    monkeypatch.setattr(
        live_paper,
        "run_live_paper_analysis",
        lambda **kwargs: {
            "status": "PAPER_ACCEPTED",
            "analysis": {
                "status": "VALID",
                "paper_order": {
                    "status": "OPEN",
                    "signal": "BUY",
                    "entry": 100.0,
                    "stop_loss": 95.0,
                    "take_profit": 110.0,
                    "pnl": 0,
                },
            },
            "execution": {
                "status": "PAPER_ACCEPTED",
                "order": {
                    "status": "OPEN",
                    "signal": "BUY",
                    "entry": 100.0,
                    "stop_loss": 95.0,
                    "take_profit": 110.0,
                    "pnl": 0,
                    "risk_amount": 5.0,
                },
            },
        },
    )

    result = live_paper.run_live_paper_session(
        symbol="BTC/USD",
        mode="scalping",
        session=session,
        account_balance=10000,
        risk_percent=1.0,
    )

    assert result["status"] == "PAPER_SESSION_ACCEPTED"
    assert len(session["orders"]) == 1
    assert session["orders"][0]["status"] == "OPEN"

    update_result = update_session_orders(
        session,
        [
            {
                "high": 112.0,
                "low": 99.0,
            }
        ],
    )

    assert update_result["status"] == "UPDATED"
    assert update_result["orders_updated"] == 1
    assert update_result["orders_closed"] == 1

    order = session["orders"][0]

    assert order["status"] == "CLOSED"
    assert order["result"] == "WIN"
    assert order["exit_price"] == 110.0
    assert order["pnl"] == 10.0

    snapshot = get_session_snapshot(session)

    assert snapshot["status"] == "VALID"
    assert snapshot["session_status"] == "READY"
    assert snapshot["orders"] == 1
    assert snapshot["open_trades"] == 0
    assert snapshot["performance"]["total_trades"] == 1
    assert snapshot["performance"]["winning_trades"] == 1
    assert snapshot["performance"]["losing_trades"] == 0
    assert snapshot["performance"]["net_pnl"] == 10.0
    assert snapshot["performance"]["starting_equity"] == 10000.0
    assert snapshot["performance"]["ending_equity"] == 10010.0
    assert snapshot["performance"]["average_r"] == 2.0


def test_end_to_end_rejected_execution_does_not_create_session_order(
    monkeypatch,
):
    import analysis.live_paper as live_paper

    from analysis.paper_session import (
        create_paper_session,
        get_session_snapshot,
    )

    session = create_paper_session(
        symbol="BTC/USD",
        mode="scalping",
        starting_balance=10000,
    )

    monkeypatch.setattr(
        live_paper,
        "run_live_paper_analysis",
        lambda **kwargs: {
            "status": "REJECTED",
            "analysis": {
                "status": "VALID",
            },
            "execution": {
                "status": "REJECTED",
                "reason": "Execution rejected",
            },
        },
    )

    result = live_paper.run_live_paper_session(
        symbol="BTC/USD",
        mode="scalping",
        session=session,
    )

    assert result["status"] == "REJECTED"
    assert len(session["orders"]) == 0

    snapshot = get_session_snapshot(session)

    assert snapshot["status"] == "VALID"
    assert snapshot["orders"] == 0
    assert snapshot["open_trades"] == 0
    assert snapshot["performance"]["total_trades"] == 0
    assert snapshot["performance"]["net_pnl"] == 0.0


def test_end_to_end_no_trade_keeps_session_unchanged(monkeypatch):
    import analysis.live_paper as live_paper

    from analysis.paper_session import (
        create_paper_session,
        get_session_snapshot,
    )

    session = create_paper_session(
        symbol="BTC/USD",
        mode="scalping",
        starting_balance=10000,
    )

    monkeypatch.setattr(
        live_paper,
        "run_live_paper_analysis",
        lambda **kwargs: {
            "status": "NO_TRADE",
            "analysis": {
                "status": "VALID",
                "paper_order": None,
            },
            "execution": None,
        },
    )

    result = live_paper.run_live_paper_session(
        symbol="BTC/USD",
        mode="scalping",
        session=session,
    )

    assert result["status"] == "NO_TRADE"
    assert len(session["orders"]) == 0

    snapshot = get_session_snapshot(session)

    assert snapshot["orders"] == 0
    assert snapshot["open_trades"] == 0
    assert snapshot["performance"]["ending_equity"] == 10000.0


def test_end_to_end_session_close_returns_final_performance():
    from analysis.paper_session import (
        add_session_order,
        close_paper_session,
        create_paper_session,
    )

    session = create_paper_session(
        symbol="BTC/USD",
        mode="scalping",
        starting_balance=10000,
    )

    add_session_order(
        session,
        {
            "status": "CLOSED",
            "signal": "BUY",
            "entry": 100.0,
            "stop_loss": 95.0,
            "take_profit": 110.0,
            "exit_price": 110.0,
            "result": "WIN",
            "pnl": 10.0,
            "risk_amount": 5.0,
        },
    )

    result = close_paper_session(session)

    assert result["status"] == "CLOSED"
    assert result["performance"]["total_trades"] == 1
    assert result["performance"]["net_pnl"] == 10.0
    assert result["performance"]["ending_equity"] == 10010.0
    assert session["status"] == "CLOSED"
