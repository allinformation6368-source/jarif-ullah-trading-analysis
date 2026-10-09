from analysis.validation.signal_validator import validate_signal


def result(decision="WAIT", fresh=True, valid=True):
    return {
        "decision": decision,
        "fresh": fresh,
        "valid": valid,
    }


def test_aligned_bullish():
    output = validate_signal(
        {
            "5min": result("BUY"),
            "15min": result("BUY"),
            "1h": result("BUY"),
        },
        required_timeframes=["5min", "15min", "1h"],
    )

    assert output["decision"] == "BUY"
    assert output["aligned"] is True
    assert output["contradiction"] is False

    print("test_aligned_bullish: PASS")


def test_aligned_bearish():
    output = validate_signal(
        {
            "5min": result("SELL"),
            "15min": result("SELL"),
            "1h": result("SELL"),
        },
        required_timeframes=["5min", "15min", "1h"],
    )

    assert output["decision"] == "SELL"
    assert output["aligned"] is True
    assert output["contradiction"] is False

    print("test_aligned_bearish: PASS")


def test_contradiction_invalidates():
    output = validate_signal(
        {
            "5min": result("BUY"),
            "15min": result("SELL"),
            "1h": result("BUY"),
        },
        required_timeframes=["5min", "15min", "1h"],
    )

    assert output["decision"] == "INVALIDATED"
    assert output["contradiction"] is True
    assert output["aligned"] is False

    print("test_contradiction_invalidates: PASS")


def test_stale_data_waits():
    output = validate_signal(
        {
            "5min": result("BUY", fresh=False),
            "15min": result("BUY"),
        },
        required_timeframes=["5min", "15min"],
    )

    assert output["decision"] == "WAIT"
    assert output["reason"] == "STALE_DATA"

    print("test_stale_data_waits: PASS")


def test_missing_timeframe_waits():
    output = validate_signal(
        {
            "5min": result("BUY"),
        },
        required_timeframes=["5min", "15min"],
    )

    assert output["decision"] == "WAIT"
    assert output["reason"] == "MISSING_TIMEFRAME"
    assert "15min" in output["missing_timeframes"]

    print("test_missing_timeframe_waits: PASS")


def test_invalid_data_waits():
    output = validate_signal(
        {
            "5min": result("BUY", valid=False),
            "15min": result("BUY"),
        },
        required_timeframes=["5min", "15min"],
    )

    assert output["decision"] == "WAIT"
    assert output["reason"] == "INVALID_DATA"

    print("test_invalid_data_waits: PASS")


def test_neutral_waits():
    output = validate_signal(
        {
            "5min": result("WAIT"),
            "15min": result("WAIT"),
        },
        required_timeframes=["5min", "15min"],
    )

    assert output["decision"] == "WAIT"
    assert output["aligned"] is False
    assert output["contradiction"] is False

    print("test_neutral_waits: PASS")


def test_no_execution_contract():
    output = validate_signal(
        {
            "5min": result("BUY"),
            "15min": result("BUY"),
        },
        required_timeframes=["5min", "15min"],
    )

    forbidden = {
        "order",
        "execute",
        "execution",
        "position",
        "trade_id",
    }

    assert forbidden.isdisjoint(output.keys())

    print("test_no_execution_contract: PASS")


if __name__ == "__main__":
    test_aligned_bullish()
    test_aligned_bearish()
    test_contradiction_invalidates()
    test_stale_data_waits()
    test_missing_timeframe_waits()
    test_invalid_data_waits()
    test_neutral_waits()
    test_no_execution_contract()

    print("STEP 10 SIGNAL VALIDATION TESTS: PASS")
