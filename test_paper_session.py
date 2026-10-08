from analysis.paper_session import (
    add_session_order,
    close_paper_session,
    create_paper_session,
    get_session_performance,
)


def test_create_paper_session():
    session = create_paper_session(
        symbol="BTC/USD",
        mode="scalping",
        starting_balance=10000,
        timestamp="2026-01-01T00:00:00+00:00",
    )

    assert session["status"] == "READY"
    assert session["symbol"] == "BTC/USD"
    assert session["mode"] == "scalping"
    assert session["starting_balance"] == 10000.0
    assert session["orders"] == []


def test_create_paper_session_rejects_invalid_balance():
    result = create_paper_session(starting_balance=0)

    assert result["status"] == "REJECTED"


def test_add_session_order():
    session = create_paper_session()

    result = add_session_order(
        session,
        {
            "status": "CLOSED",
            "signal": "BUY",
            "pnl": 100.0,
            "risk_amount": 50.0,
        },
    )

    assert result["status"] == "ADDED"
    assert result["orders"] == 1
    assert len(session["orders"]) == 1


def test_session_performance_uses_closed_orders():
    session = create_paper_session(
        symbol="BTC/USD",
        mode="scalping",
        starting_balance=10000,
        timestamp="2026-01-01T00:00:00+00:00",
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

    add_session_order(
        session,
        {
            "status": "OPEN",
            "signal": "BUY",
            "pnl": 0,
        },
    )

    result = get_session_performance(session)

    assert result["status"] == "VALID"
    assert result["symbol"] == "BTC/USD"
    assert result["mode"] == "scalping"
    assert result["performance"]["total_trades"] == 2
    assert result["performance"]["net_pnl"] == 60.0
    assert result["performance"]["open_trades"] == 1
    assert result["performance"]["ending_equity"] == 10060.0


def test_empty_session_performance():
    session = create_paper_session(starting_balance=10000)

    result = get_session_performance(session)

    assert result["status"] == "VALID"
    assert result["performance"]["total_trades"] == 0
    assert result["performance"]["net_pnl"] == 0.0
    assert result["performance"]["ending_equity"] == 10000.0


def test_invalid_session_is_rejected():
    result = get_session_performance(None)

    assert result["status"] == "REJECTED"


def test_add_invalid_order_is_rejected():
    session = create_paper_session()

    result = add_session_order(session, None)

    assert result["status"] == "REJECTED"


def test_close_session_returns_final_performance():
    session = create_paper_session(
        symbol="BTC/USD",
        mode="intraday",
        starting_balance=10000,
        timestamp="2026-01-01T00:00:00+00:00",
    )

    add_session_order(
        session,
        {
            "status": "CLOSED",
            "signal": "BUY",
            "pnl": 150.0,
            "risk_amount": 50.0,
        },
    )

    result = close_paper_session(session)

    assert result["status"] == "CLOSED"
    assert session["status"] == "CLOSED"
    assert result["performance"]["net_pnl"] == 150.0
    assert result["performance"]["ending_equity"] == 10150.0


def test_closed_session_cannot_accept_new_order():
    session = create_paper_session()

    close_paper_session(session)

    result = add_session_order(
        session,
        {
            "status": "CLOSED",
            "pnl": 10.0,
        },
    )

    assert result["status"] == "REJECTED"
