from analysis.scanner.intelligence import evaluate_candidate


def tf(decision):
    return {
        "decision": decision,
        "fresh": True,
        "valid": True,
    }


def mtf(decision, contradiction=False, aligned=True):
    return {
        "decision": decision,
        "valid": True,
        "aligned": aligned,
        "contradiction": contradiction,
        "directions": {
            "5min": "BULLISH" if decision == "BUY" else "BEARISH",
            "15min": "BULLISH" if decision == "BUY" else "BEARISH",
        },
    }


def risk(valid=True):
    return {
        "valid": valid,
    }


def test_buy_candidate():
    result = evaluate_candidate(
        pair="BTC/USD",
        timeframe_results={
            "5min": tf("BUY"),
            "15min": tf("BUY"),
        },
        mtf_validation=mtf("BUY"),
        confluence={"decision": "BUY", "score": 5},
        risk_validation=risk(True),
    )

    assert result["decision"] == "BUY"
    assert result["candidate"] is True
    assert result["reason"] == "CANDIDATE_ALIGNED"
    assert result["risk_checked"] is True
    assert result["risk_valid"] is True

    print("test_buy_candidate: PASS")


def test_sell_candidate():
    result = evaluate_candidate(
        pair="EUR/USD",
        timeframe_results={
            "5min": tf("SELL"),
            "15min": tf("SELL"),
        },
        mtf_validation=mtf("SELL"),
        confluence={"decision": "SELL", "score": -5},
        risk_validation=risk(True),
    )

    assert result["decision"] == "SELL"
    assert result["candidate"] is True

    print("test_sell_candidate: PASS")


def test_contradiction_invalidates():
    result = evaluate_candidate(
        pair="GBP/USD",
        timeframe_results={
            "5min": tf("BUY"),
            "15min": tf("SELL"),
        },
        mtf_validation=mtf(
            "INVALIDATED",
            contradiction=True,
            aligned=False,
        ),
        confluence={
            "decision": "INVALIDATED",
            "score": 0,
        },
        risk_validation=risk(True),
    )

    assert result["decision"] == "INVALIDATED"
    assert result["candidate"] is False
    assert result["contradiction"] is True

    print("test_contradiction_invalidates: PASS")


def test_without_risk_validation_waits():
    result = evaluate_candidate(
        pair="USD/JPY",
        timeframe_results={
            "5min": tf("BUY"),
            "15min": tf("BUY"),
        },
        mtf_validation=mtf("BUY"),
        confluence={"decision": "BUY", "score": 5},
        risk_validation=None,
    )

    assert result["decision"] == "WAIT"
    assert result["candidate"] is False
    assert result["reason"] == "RISK_NOT_VALIDATED"

    print("test_without_risk_validation_waits: PASS")


def test_risk_blocked():
    result = evaluate_candidate(
        pair="USD/CHF",
        timeframe_results={
            "5min": tf("BUY"),
            "15min": tf("BUY"),
        },
        mtf_validation=mtf("BUY"),
        confluence={"decision": "BUY", "score": 5},
        risk_validation=risk(False),
    )

    assert result["decision"] == "WAIT"
    assert result["candidate"] is False
    assert result["reason"] == "RISK_BLOCKED"

    print("test_risk_blocked: PASS")


def test_wait_is_not_candidate():
    result = evaluate_candidate(
        pair="AUD/USD",
        timeframe_results={
            "5min": tf("WAIT"),
            "15min": tf("WAIT"),
        },
        mtf_validation=mtf(
            "WAIT",
            aligned=False,
        ),
        confluence={"decision": "WAIT", "score": 0},
        risk_validation=None,
    )

    assert result["decision"] == "WAIT"
    assert result["candidate"] is False

    print("test_wait_is_not_candidate: PASS")


def test_setup_key():
    result = evaluate_candidate(
        pair="USD/CAD",
        timeframe_results={
            "5min": tf("BUY"),
        },
        mtf_validation=mtf("BUY"),
        confluence={"decision": "BUY", "score": 4},
        risk_validation=risk(True),
    )

    assert result["setup_key"] == "USD/CAD|BUY"

    print("test_setup_key: PASS")


def test_no_api_or_execution_keys():
    result = evaluate_candidate(
        pair="ETH/USD",
        timeframe_results={
            "5min": tf("BUY"),
        },
        mtf_validation=mtf("BUY"),
        confluence={"decision": "BUY", "score": 4},
        risk_validation=risk(True),
    )

    forbidden = {
        "order",
        "execute",
        "execution",
        "broker",
        "api_request",
        "request",
    }

    assert forbidden.isdisjoint(result.keys())

    print("test_no_api_or_execution_keys: PASS")


if __name__ == "__main__":
    test_buy_candidate()
    test_sell_candidate()
    test_contradiction_invalidates()
    test_without_risk_validation_waits()
    test_risk_blocked()
    test_wait_is_not_candidate()
    test_setup_key()
    test_no_api_or_execution_keys()

    print("STEP 12A SCANNER INTELLIGENCE TESTS: PASS")
