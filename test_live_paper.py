from analysis.live_paper import run_live_paper_analysis


def test_run_live_paper_analysis_accepts_paper_order(monkeypatch):
    def fake_analyze(**kwargs):
        return {
            "status": "VALID",
            "symbol": kwargs["symbol"],
            "mode": kwargs["mode"],
            "analysis": {
                "paper_order": {
                    "signal": "BUY",
                    "entry": 100.0,
                    "stop_loss": 95.0,
                    "take_profit": 110.0,
                }
            },
        }

    def fake_execute(**kwargs):
        assert kwargs["mode"] == "PAPER"
        assert kwargs["order"]["signal"] == "BUY"

        return {
            "status": "PAPER_ACCEPTED",
            "signal": "BUY",
        }

    monkeypatch.setattr(
        "analysis.live_paper.analyze_live_market",
        fake_analyze,
    )
    monkeypatch.setattr(
        "analysis.live_paper.execute_order",
        fake_execute,
    )

    result = run_live_paper_analysis(
        symbol="BTC/USD",
        mode="scalping",
    )

    assert result["status"] == "PAPER_ACCEPTED"
    assert result["execution"]["signal"] == "BUY"


def test_run_live_paper_analysis_no_trade(monkeypatch):
    def fake_analyze(**kwargs):
        return {
            "status": "VALID",
            "analysis": {
                "paper_order": None,
            },
        }

    called = False

    def fake_execute(**kwargs):
        nonlocal called
        called = True
        return {}

    monkeypatch.setattr(
        "analysis.live_paper.analyze_live_market",
        fake_analyze,
    )
    monkeypatch.setattr(
        "analysis.live_paper.execute_order",
        fake_execute,
    )

    result = run_live_paper_analysis(
        symbol="BTC/USD",
        mode="scalping",
    )

    assert result["status"] == "NO_TRADE"
    assert result["execution"] is None
    assert called is False


def test_run_live_paper_analysis_rejects_analysis_failure(monkeypatch):
    def fake_analyze(**kwargs):
        return {
            "status": "REJECTED",
            "reason": "API unavailable",
        }

    called = False

    def fake_execute(**kwargs):
        nonlocal called
        called = True
        return {}

    monkeypatch.setattr(
        "analysis.live_paper.analyze_live_market",
        fake_analyze,
    )
    monkeypatch.setattr(
        "analysis.live_paper.execute_order",
        fake_execute,
    )

    result = run_live_paper_analysis(
        symbol="BTC/USD",
        mode="scalping",
    )

    assert result["status"] == "REJECTED"
    assert result["reason"] == "API unavailable"
    assert result["execution"] is None
    assert called is False


def test_run_live_paper_analysis_forwards_risk_config(monkeypatch):
    captured = {}

    def fake_analyze(**kwargs):
        captured.update(kwargs)

        return {
            "status": "VALID",
            "analysis": {
                "paper_order": None,
            },
        }

    monkeypatch.setattr(
        "analysis.live_paper.analyze_live_market",
        fake_analyze,
    )

    result = run_live_paper_analysis(
        symbol="ETH/USD",
        mode="intraday",
        account_balance=25000,
        risk_percent=1.5,
        outputsize=200,
    )

    assert result["status"] == "NO_TRADE"
    assert captured["symbol"] == "ETH/USD"
    assert captured["mode"] == "intraday"
    assert captured["account_balance"] == 25000
    assert captured["risk_percent"] == 1.5
    assert captured["outputsize"] == 200


def test_run_live_paper_analysis_forced_entry_to_execution(monkeypatch):
    def fake_analyze(**kwargs):
        return {
            "status": "VALID",
            "symbol": kwargs["symbol"],
            "mode": kwargs["mode"],
            "analysis": {
                "paper_order": {
                    "signal": "SELL",
                    "entry": 100.0,
                    "stop_loss": 105.0,
                    "take_profit": 90.0,
                }
            },
        }

    captured = {}

    def fake_execute(**kwargs):
        captured.update(kwargs)

        return {
            "status": "PAPER_ACCEPTED",
            "signal": kwargs["order"]["signal"],
        }

    monkeypatch.setattr(
        "analysis.live_paper.analyze_live_market",
        fake_analyze,
    )
    monkeypatch.setattr(
        "analysis.live_paper.execute_order",
        fake_execute,
    )

    result = run_live_paper_analysis(
        symbol="BTC/USD",
        mode="scalping",
        account_balance=10000,
        risk_percent=1.0,
    )

    assert result["status"] == "PAPER_ACCEPTED"
    assert result["symbol"] == "BTC/USD"
    assert result["mode"] == "scalping"
    assert result["execution"]["status"] == "PAPER_ACCEPTED"
    assert captured["mode"] == "PAPER"
    assert captured["order"]["signal"] == "SELL"


def test_no_trade_preserves_symbol_and_mode(monkeypatch):
    def fake_analyze(**kwargs):
        return {
            "status": "VALID",
            "analysis": {
                "paper_order": None,
            },
        }

    monkeypatch.setattr(
        "analysis.live_paper.analyze_live_market",
        fake_analyze,
    )

    result = run_live_paper_analysis(
        symbol="ETH/USD",
        mode="intraday",
    )

    assert result["status"] == "NO_TRADE"
    assert result["symbol"] == "ETH/USD"
    assert result["mode"] == "intraday"


def test_live_paper_session_rejects_invalid_session():
    from analysis.live_paper import run_live_paper_session

    result = run_live_paper_session(
        symbol="BTC/USD",
        mode="scalping",
        session=None,
    )

    assert result["status"] == "REJECTED"


def test_live_paper_session_rejects_closed_session(monkeypatch):
    from analysis.live_paper import run_live_paper_session

    session = {
        "status": "CLOSED",
        "orders": [],
    }

    result = run_live_paper_session(
        symbol="BTC/USD",
        mode="scalping",
        session=session,
    )

    assert result["status"] == "REJECTED"


def test_live_paper_session_adds_accepted_order(monkeypatch):
    import analysis.live_paper as live_paper

    session = {
        "status": "READY",
        "symbol": "BTC/USD",
        "mode": "scalping",
        "starting_balance": 10000.0,
        "orders": [],
    }

    monkeypatch.setattr(
        live_paper,
        "run_live_paper_analysis",
        lambda **kwargs: {
            "status": "PAPER_ACCEPTED",
            "analysis": {
                "paper_order": {
                    "status": "OPEN",
                    "signal": "BUY",
                    "entry": 100.0,
                    "stop_loss": 95.0,
                    "take_profit": 110.0,
                    "pnl": 0,
                }
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
                },
            },
        },
    )

    result = live_paper.run_live_paper_session(
        symbol="BTC/USD",
        mode="scalping",
        session=session,
    )

    assert result["status"] == "PAPER_SESSION_ACCEPTED"
    assert result["session"]["status"] == "ADDED"
    assert len(session["orders"]) == 1
    assert session["orders"][0]["signal"] == "BUY"


def test_live_paper_session_does_not_add_rejected_execution(monkeypatch):
    import analysis.live_paper as live_paper

    session = {
        "status": "READY",
        "orders": [],
    }

    monkeypatch.setattr(
        live_paper,
        "run_live_paper_analysis",
        lambda **kwargs: {
            "status": "REJECTED",
            "analysis": {},
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


def test_live_paper_session_handles_no_trade(monkeypatch):
    import analysis.live_paper as live_paper

    session = {
        "status": "READY",
        "orders": [],
    }

    monkeypatch.setattr(
        live_paper,
        "run_live_paper_analysis",
        lambda **kwargs: {
            "status": "NO_TRADE",
            "analysis": {},
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
