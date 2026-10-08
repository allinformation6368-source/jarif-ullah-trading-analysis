from analysis.live_mtf import analyze_live_market


def test_analyze_live_market(monkeypatch):
    def fake_fetch(
        symbol,
        mode,
        outputsize,
        provider,
    ):
        return {
            "status": "VALID",
            "symbol": symbol,
            "mode": mode,
            "timeframes": {
                "1min": [{"close": 100}],
                "5min": [{"close": 101}],
                "15min": [{"close": 102}],
                "1h": [{"close": 103}],
            },
        }

    def fake_analyze(
        timeframes,
        mode,
        account_balance,
        risk_percent,
    ):
        assert set(timeframes) == {
            "1min",
            "5min",
            "15min",
            "1h",
        }
        assert mode == "scalping"
        assert account_balance == 10000
        assert risk_percent == 1

        return {
            "decision": {
                "decision": "WAIT",
                "signal": None,
            }
        }

    monkeypatch.setattr(
        "analysis.live_mtf.fetch_mode_market_data",
        fake_fetch,
    )
    monkeypatch.setattr(
        "analysis.live_mtf.analyze_multi_timeframe",
        fake_analyze,
    )

    result = analyze_live_market(
        symbol="BTC/USD",
        mode="scalping",
        account_balance=10000,
        risk_percent=1,
        outputsize=100,
    )

    assert result["status"] == "VALID"
    assert result["symbol"] == "BTC/USD"
    assert result["mode"] == "scalping"
    assert result["analysis"]["decision"]["decision"] == "WAIT"


def test_analyze_live_market_rejects_data_failure(monkeypatch):
    called = False

    def fake_fetch(*args, **kwargs):
        return {
            "status": "REJECTED",
            "reason": "API unavailable",
        }

    def fake_analyze(*args, **kwargs):
        nonlocal called
        called = True
        return {}

    monkeypatch.setattr(
        "analysis.live_mtf.fetch_mode_market_data",
        fake_fetch,
    )
    monkeypatch.setattr(
        "analysis.live_mtf.analyze_multi_timeframe",
        fake_analyze,
    )

    result = analyze_live_market(
        symbol="BTC/USD",
        mode="scalping",
    )

    assert result["status"] == "REJECTED"
    assert result["reason"] == "API unavailable"
    assert called is False


def test_analyze_live_market_forwards_risk_config(monkeypatch):
    captured = {}

    def fake_fetch(*args, **kwargs):
        return {
            "status": "VALID",
            "timeframes": {
                "5min": [],
                "15min": [],
                "1h": [],
                "4h": [],
            },
        }

    def fake_analyze(**kwargs):
        captured.update(kwargs)
        return {"decision": {"decision": "WAIT"}}

    monkeypatch.setattr(
        "analysis.live_mtf.fetch_mode_market_data",
        fake_fetch,
    )
    monkeypatch.setattr(
        "analysis.live_mtf.analyze_multi_timeframe",
        fake_analyze,
    )

    result = analyze_live_market(
        symbol="BTC/USD",
        mode="intraday",
        account_balance=25000,
        risk_percent=1.5,
        outputsize=200,
    )

    assert result["status"] == "VALID"
    assert captured["mode"] == "intraday"
    assert captured["account_balance"] == 25000
    assert captured["risk_percent"] == 1.5


def test_analyze_live_market_propagates_provider(monkeypatch):
    captured = {}

    def fake_fetch(**kwargs):
        captured.update(kwargs)
        return {
            "status": "VALID",
            "timeframes": {},
        }

    monkeypatch.setattr(
        "analysis.live_mtf.fetch_mode_market_data",
        fake_fetch,
    )
    monkeypatch.setattr(
        "analysis.live_mtf.analyze_multi_timeframe",
        lambda **kwargs: {},
    )

    result = analyze_live_market(
        symbol="ETH/USD",
        mode="swing",
        provider="twelvedata",
    )

    assert result["status"] == "VALID"
    assert captured["provider"] == "twelvedata"
    assert captured["symbol"] == "ETH/USD"
    assert captured["mode"] == "swing"
