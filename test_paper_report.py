from analysis.paper_report import generate_paper_report
from analysis.paper_session import (
    add_session_order,
    create_paper_session,
)


def test_generate_paper_report():
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
        {
            "status": "REJECTED",
            "mode": "PAPER",
            "reason": "Risk rejected",
        },
    ]

    report = generate_paper_report(
        session,
        audits,
    )

    assert report["status"] == "VALID"
    assert report["symbol"] == "BTC/USD"
    assert report["mode"] == "scalping"
    assert report["orders"] == 2
    assert report["open_trades"] == 1
    assert report["closed_trades"] == 1

    assert report["execution"]["audit_count"] == 3
    assert report["execution"]["accepted"] == 2
    assert report["execution"]["rejected"] == 1

    assert report["performance"]["starting_equity"] == 10000.0
    assert report["performance"]["ending_equity"] == 10010.0
    assert report["performance"]["net_pnl"] == 10.0
    assert report["performance"]["win_rate"] == 100.0
    assert report["performance"]["average_r"] == 2.0


def test_generate_paper_report_empty_session():
    session = create_paper_session(
        symbol="BTC/USD",
        mode="scalping",
        starting_balance=10000,
    )

    report = generate_paper_report(
        session,
        [],
    )

    assert report["status"] == "VALID"
    assert report["orders"] == 0
    assert report["open_trades"] == 0
    assert report["closed_trades"] == 0
    assert report["execution"]["audit_count"] == 0
    assert report["execution"]["accepted"] == 0
    assert report["execution"]["rejected"] == 0
    assert report["performance"]["net_pnl"] == 0.0
    assert report["performance"]["ending_equity"] == 10000.0


def test_generate_paper_report_rejects_invalid_session():
    result = generate_paper_report(
        None,
        [],
    )

    assert result["status"] == "REJECTED"


def test_generate_paper_report_rejects_invalid_audits():
    session = create_paper_session()

    result = generate_paper_report(
        session,
        None,
    )

    assert result["status"] == "REJECTED"


def test_generate_paper_report_contains_drawdown_and_profit_factor():
    session = create_paper_session(
        starting_balance=10000,
    )

    add_session_order(
        session,
        {
            "status": "CLOSED",
            "signal": "BUY",
            "pnl": 100.0,
            "risk_amount": 50.0,
        },
    )

    add_session_order(
        session,
        {
            "status": "CLOSED",
            "signal": "SELL",
            "pnl": -40.0,
            "risk_amount": 50.0,
        },
    )

    report = generate_paper_report(
        session,
        [
            {
                "status": "PAPER_ACCEPTED",
                "mode": "PAPER",
            },
            {
                "status": "PAPER_ACCEPTED",
                "mode": "PAPER",
            },
        ],
    )

    assert report["status"] == "VALID"
    assert report["performance"]["net_pnl"] == 60.0
    assert report["performance"]["profit_factor"] == 2.5
    assert report["performance"]["max_drawdown"] == 40.0
    assert report["performance"]["average_pnl"] == 30.0
