from analysis.mtf_engine import analyze_multi_timeframe


timeframes = {
    "5m": [],
    "15m": [],
    "1h": [],
}


try:
    result = analyze_multi_timeframe(timeframes)

    print("MTF ENGINE TEST: SUCCESS")
    print("Result type:", type(result).__name__)
    print("Timeframes:", list(result["timeframes"].keys()))

    for timeframe, analysis in result["timeframes"].items():
        print(
            timeframe,
            "->",
            analysis["confluence"]["signal"]
        )

    print("FINAL SIGNAL:", result["confluence"]["signal"])
    print("FINAL SCORE:", result["confluence"]["score"])
    print("FINAL CONFIDENCE:", result["confluence"]["confidence"])

except Exception as e:
    print("MTF ENGINE TEST: FAILED")
    print(type(e).__name__, ":", e)


def test_mtf_engine_creates_paper_order(monkeypatch):
    import analysis.mtf_engine as mtf_engine

    candles = [
        {
            "open": 100,
            "high": 102,
            "low": 99,
            "close": 101,
        }
    ]

    trade_plan = {
        "status": "READY",
        "signal": "BUY",
        "entry": 100,
        "stop_loss": 95,
        "take_profit": 110,
        "risk": 5,
        "reward": 10,
        "risk_reward": 2,
    }

    monkeypatch.setattr(
        mtf_engine,
        "analyze_timeframe",
        lambda candles: {"status": "VALID"},
    )
    monkeypatch.setattr(
        mtf_engine,
        "calculate_mtf_confluence",
        lambda results, mode=None: {},
    )
    monkeypatch.setattr(
        mtf_engine,
        "evaluate_trade_decision",
        lambda confluence: {
            "decision": "WAIT",
            "signal": "BUY",
        },
    )
    monkeypatch.setattr(
        mtf_engine,
        "evaluate_entry_quality",
        lambda confluence, decision: None,
    )
    monkeypatch.setattr(
        mtf_engine,
        "build_unified_trade_plan",
        lambda **kwargs: trade_plan,
    )
    monkeypatch.setattr(
        mtf_engine,
        "create_trade_record",
        lambda **kwargs: {
            "status": "RECORDED",
        },
    )

    result = mtf_engine.analyze_multi_timeframe(
        {"M15": candles},
        account_balance=10000,
        risk_percent=1,
    )

    assert result["trade_plan"]["status"] == "READY"
    assert result["paper_order"]["status"] == "OPEN"
    assert result["paper_order"]["signal"] == "BUY"
    assert result["paper_order"]["account_balance"] == 10000


def test_mtf_engine_no_paper_order_when_trade_not_ready():
    from analysis.mtf_engine import analyze_multi_timeframe

    result = analyze_multi_timeframe(
        {"M15": []},
        account_balance=10000,
        risk_percent=1,
    )

    assert result["trade_plan"]["status"] != "READY"
    assert result["paper_order"] is None
