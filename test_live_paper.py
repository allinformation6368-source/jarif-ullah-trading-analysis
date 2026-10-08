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
