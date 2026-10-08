def test_full_trading_system_integration(monkeypatch):
    import analysis.live_paper as live_paper

    from analysis.paper_report import generate_paper_report
    from analysis.paper_session import (
        create_paper_session,
        update_session_orders,
    )

    session = create_paper_session(
        symbol="BTC/USD",
        mode="scalping",
        starting_balance=10000,
        timestamp="2026-01-01T00:00:00+00:00",
    )

    def fake_live_analysis(**kwargs):
        return {
            "status": "PAPER_ACCEPTED",
            "analysis": {
                "status": "VALID",
                "signal": "BUY",
                "confidence": 85,
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
        }

    monkeypatch.setattr(
        live_paper,
        "run_live_paper_analysis",
        fake_live_analysis,
    )

    execution_result = live_paper.run_live_paper_session(
        symbol="BTC/USD",
        mode="scalping",
        session=session,
        account_balance=10000,
        risk_percent=1.0,
    )

    assert execution_result["status"] == "PAPER_SESSION_ACCEPTED"
    assert len(session["orders"]) == 1
    assert session["orders"][0]["status"] == "OPEN"

    candle_result = update_session_orders(
        session,
        [
            {
                "open": 100.0,
                "high": 112.0,
                "low": 99.0,
                "close": 110.0,
            }
        ],
    )

    assert candle_result["status"] == "UPDATED"
    assert candle_result["orders_updated"] == 1
    assert candle_result["orders_closed"] == 1

    order = session["orders"][0]

    assert order["status"] == "CLOSED"
    assert order["result"] == "WIN"
    assert order["exit_price"] == 110.0
    assert order["pnl"] == 10.0

    audits = [
        {
            "status": "PAPER_ACCEPTED",
            "mode": "PAPER",
            "signal": "BUY",
        }
    ]

    report = generate_paper_report(
        session,
        audits,
    )

    assert report["status"] == "VALID"
    assert report["symbol"] == "BTC/USD"
    assert report["mode"] == "scalping"

    assert report["orders"] == 1
    assert report["open_trades"] == 0
    assert report["closed_trades"] == 1

    assert report["execution"]["audit_count"] == 1
    assert report["execution"]["accepted"] == 1
    assert report["execution"]["rejected"] == 0

    assert report["performance"]["starting_equity"] == 10000.0
    assert report["performance"]["ending_equity"] == 10010.0
    assert report["performance"]["net_pnl"] == 10.0
    assert report["performance"]["win_rate"] == 100.0
    assert report["performance"]["profit_factor"] == float("inf")
    assert report["performance"]["max_drawdown"] == 0.0
    assert report["performance"]["average_pnl"] == 10.0
    assert report["performance"]["average_r"] == 2.0


def test_full_system_rejection_path(monkeypatch):
    import analysis.live_paper as live_paper

    from analysis.paper_report import generate_paper_report
    from analysis.paper_session import (
        create_paper_session,
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
                "reason": "Invalid signal",
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

    report = generate_paper_report(
        session,
        [
            {
                "status": "REJECTED",
                "mode": "PAPER",
                "reason": "Invalid signal",
            }
        ],
    )

    assert report["status"] == "VALID"
    assert report["orders"] == 0
    assert report["closed_trades"] == 0
    assert report["execution"]["audit_count"] == 1
    assert report["execution"]["accepted"] == 0
    assert report["execution"]["rejected"] == 1
    assert report["performance"]["net_pnl"] == 0.0
    assert report["performance"]["ending_equity"] == 10000.0
