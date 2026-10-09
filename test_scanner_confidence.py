from analysis.scanner.confidence import evaluate_confidence


def test_high_confidence():
    result = evaluate_confidence(
        decision="BUY",
        confluence={"score": 8},
        mtf_validation={
            "aligned": True,
            "contradiction": False,
        },
        risk_validation={"valid": True},
    )

    assert result["confidence"] == 100
    assert result["quality"] == "HIGH"
    assert result["qualified"] is True

    print("test_high_confidence: PASS")


def test_medium_confidence():
    result = evaluate_confidence(
        decision="BUY",
        confluence={"score": 6},
        mtf_validation={
            "aligned": True,
            "contradiction": False,
        },
        risk_validation={"valid": True},
    )

    assert result["confidence"] == 90
    assert result["quality"] == "HIGH"
    assert result["qualified"] is True

    print("test_medium_confidence: PASS")


def test_low_confidence():
    result = evaluate_confidence(
        decision="BUY",
        confluence={"score": 2},
        mtf_validation={
            "aligned": False,
            "contradiction": False,
        },
        risk_validation={"valid": True},
    )

    assert result["confidence"] == 40
    assert result["quality"] == "LOW"
    assert result["qualified"] is False

    print("test_low_confidence: PASS")


def test_risk_failure():
    result = evaluate_confidence(
        decision="SELL",
        confluence={"score": 8},
        mtf_validation={
            "aligned": True,
            "contradiction": False,
        },
        risk_validation={"valid": False},
    )

    assert result["quality"] == "LOW"
    assert result["qualified"] is False
    assert result["reason"] == "RISK_NOT_VALIDATED"

    print("test_risk_failure: PASS")


def test_contradiction():
    result = evaluate_confidence(
        decision="BUY",
        confluence={"score": 8},
        mtf_validation={
            "aligned": False,
            "contradiction": True,
        },
        risk_validation={"valid": True},
    )

    assert result["quality"] == "LOW"
    assert result["qualified"] is False
    assert result["reason"] == "MTF_CONTRADICTION"

    print("test_contradiction: PASS")


def test_wait():
    result = evaluate_confidence(
        decision="WAIT",
        confluence={"score": 8},
        mtf_validation={
            "aligned": True,
            "contradiction": False,
        },
        risk_validation={"valid": True},
    )

    assert result["confidence"] == 0
    assert result["quality"] == "LOW"
    assert result["qualified"] is False

    print("test_wait: PASS")


def test_invalidated():
    result = evaluate_confidence(
        decision="INVALIDATED",
        confluence={"score": 8},
        mtf_validation={
            "aligned": True,
            "contradiction": False,
        },
        risk_validation={"valid": True},
    )

    assert result["confidence"] == 0
    assert result["qualified"] is False

    print("test_invalidated: PASS")


def test_no_execution_keys():
    result = evaluate_confidence(
        decision="BUY",
        confluence={"score": 4},
        mtf_validation={
            "aligned": True,
            "contradiction": False,
        },
        risk_validation={"valid": True},
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
    test_high_confidence()
    test_medium_confidence()
    test_low_confidence()
    test_risk_failure()
    test_contradiction()
    test_wait()
    test_invalidated()
    test_no_execution_keys()

    print("STEP 12B CONFIDENCE TESTS: PASS")
