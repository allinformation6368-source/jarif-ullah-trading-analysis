from analysis.scanner.pipeline import run_scanner_intelligence


def tf(decision, direction):
    return {
        "decision": decision,
        "valid": True,
        "fresh": True,
        "direction": direction,
    }


def mtf(decision, direction, aligned=True, contradiction=False):
    return {
        "decision": decision,
        "valid": True,
        "aligned": aligned,
        "contradiction": contradiction,
        "directions": {
            "5min": direction,
            "15min": direction,
        },
    }


def test_buy_end_to_end():
    result = run_scanner_intelligence(
        pair="BTC/USD",
        timeframe_results={
            "5min": tf("BUY", "BULLISH"),
            "15min": tf("BUY", "BULLISH"),
        },
        mtf_validation=mtf("BUY", "BULLISH"),
        confluence={
            "decision": "BUY",
            "score": 8,
        },
        risk_validation={
            "valid": True,
        },
        candle_id="btc-candle-100",
        now=1000,
    )

    assert result["decision"] == "BUY"
    assert result["candidate"] is True
    assert result["qualified"] is True
    assert result["quality"] == "HIGH"
    assert result["setup_state"] == "ACTIVE"
    assert result["risk_valid"] is True

    print("test_buy_end_to_end: PASS")


def test_sell_end_to_end():
    result = run_scanner_intelligence(
        pair="EUR/USD",
        timeframe_results={
            "5min": tf("SELL", "BEARISH"),
            "15min": tf("SELL", "BEARISH"),
        },
        mtf_validation=mtf("SELL", "BEARISH"),
        confluence={
            "decision": "SELL",
            "score": -8,
        },
        risk_validation={
            "valid": True,
        },
        candle_id="eur-candle-200",
        now=2000,
    )

    assert result["decision"] == "SELL"
    assert result["candidate"] is True
    assert result["qualified"] is True
    assert result["setup_state"] == "ACTIVE"

    print("test_sell_end_to_end: PASS")


def test_risk_failure_stops_candidate():
    result = run_scanner_intelligence(
        pair="ETH/USD",
        timeframe_results={
            "5min": tf("BUY", "BULLISH"),
            "15min": tf("BUY", "BULLISH"),
        },
        mtf_validation=mtf("BUY", "BULLISH"),
        confluence={
            "decision": "BUY",
            "score": 8,
        },
        risk_validation={
            "valid": False,
        },
        candle_id="eth-candle-300",
        now=3000,
    )

    assert result["decision"] == "WAIT"
    assert result["candidate"] is False
    assert result["qualified"] is False
    assert result["quality"] == "LOW"

    print("test_risk_failure_stops_candidate: PASS")


def test_mtf_contradiction_invalidates():
    result = run_scanner_intelligence(
        pair="GBP/USD",
        timeframe_results={
            "5min": tf("BUY", "BULLISH"),
            "15min": tf("SELL", "BEARISH"),
        },
        mtf_validation=mtf(
            "INVALIDATED",
            "MIXED",
            aligned=False,
            contradiction=True,
        ),
        confluence={
            "decision": "INVALIDATED",
            "score": 0,
        },
        risk_validation={
            "valid": True,
        },
        candle_id="gbp-candle-400",
        now=4000,
    )

    assert result["decision"] == "INVALIDATED"
    assert result["candidate"] is False
    assert result["qualified"] is False
    assert result["setup_state"] == "INVALIDATED"

    print("test_mtf_contradiction_invalidates: PASS")


def test_low_quality_is_not_qualified():
    result = run_scanner_intelligence(
        pair="USD/JPY",
        timeframe_results={
            "5min": tf("BUY", "BULLISH"),
        },
        mtf_validation=mtf(
            "BUY",
            "BULLISH",
            aligned=False,
        ),
        confluence={
            "decision": "BUY",
            "score": 2,
        },
        risk_validation={
            "valid": True,
        },
        candle_id="jpy-candle-500",
        now=5000,
    )

    assert result["decision"] == "WAIT"
    assert result["candidate"] is False
    assert result["qualified"] is False
    assert result["quality"] == "LOW"
    assert result["reason"] == "INSUFFICIENT_CONFLUENCE"

    print("test_low_quality_is_not_qualified: PASS")


def test_setup_persists_on_next_scan():
    first = run_scanner_intelligence(
        pair="USD/CAD",
        timeframe_results={
            "5min": tf("BUY", "BULLISH"),
        },
        mtf_validation=mtf("BUY", "BULLISH"),
        confluence={
            "decision": "BUY",
            "score": 8,
        },
        risk_validation={"valid": True},
        candle_id="cad-candle-600",
        previous_state="NEW",
        now=6000,
    )

    second = run_scanner_intelligence(
        pair="USD/CAD",
        timeframe_results={
            "5min": tf("BUY", "BULLISH"),
        },
        mtf_validation=mtf("BUY", "BULLISH"),
        confluence={
            "decision": "BUY",
            "score": 8,
        },
        risk_validation={"valid": True},
        candle_id="cad-candle-601",
        previous_state=first["setup_state"],
        now=6072,
    )

    assert first["setup_state"] == "ACTIVE"
    assert second["setup_state"] == "ACTIVE"
    assert second["setup_reason"] == "SETUP_STILL_ACTIVE"

    print("test_setup_persists_on_next_scan: PASS")


def test_no_execution_keys():
    result = run_scanner_intelligence(
        pair="AUD/USD",
        timeframe_results={
            "5min": tf("WAIT", "NEUTRAL"),
        },
        mtf_validation=mtf(
            "WAIT",
            "NEUTRAL",
            aligned=False,
        ),
        confluence={
            "decision": "WAIT",
            "score": 0,
        },
        risk_validation=None,
        candle_id="aud-candle-700",
        now=7000,
    )

    forbidden = {
        "order",
        "execute",
        "execution",
        "broker",
        "trade_id",
        "position",
    }

    assert forbidden.isdisjoint(result.keys())

    print("test_no_execution_keys: PASS")


if __name__ == "__main__":
    test_buy_end_to_end()
    test_sell_end_to_end()
    test_risk_failure_stops_candidate()
    test_mtf_contradiction_invalidates()
    test_low_quality_is_not_qualified()
    test_setup_persists_on_next_scan()
    test_no_execution_keys()

    print("STEP 12D PIPELINE TESTS: PASS")
