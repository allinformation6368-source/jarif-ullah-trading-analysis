from analysis.validation.risk_signal import validate_risk_signal


def signal(decision):
    return {
        "decision": decision,
        "valid": True,
    }


def test_buy_risk_validated():
    result = validate_risk_signal(
        signal("BUY"),
        {"valid": True},
        {"valid": True},
        {"allowed": True},
    )

    assert result["decision"] == "BUY"
    assert result["valid"] is True
    assert result["reason"] == "RISK_VALIDATED"

    print("test_buy_risk_validated: PASS")


def test_sell_risk_validated():
    result = validate_risk_signal(
        signal("SELL"),
        {"valid": True},
        {"valid": True},
        {"allowed": True},
    )

    assert result["decision"] == "SELL"
    assert result["valid"] is True

    print("test_sell_risk_validated: PASS")


def test_wait_has_no_risk_action():
    result = validate_risk_signal(
        signal("WAIT"),
        {"valid": False},
        {"valid": False},
        {"allowed": False},
    )

    assert result["decision"] == "WAIT"
    assert result["valid"] is True
    assert result["reason"] == "NO_RISK_ACTION"

    print("test_wait_has_no_risk_action: PASS")


def test_invalidated_has_no_risk_action():
    result = validate_risk_signal(
        signal("INVALIDATED"),
        {"valid": False},
        {"valid": False},
        {"allowed": False},
    )

    assert result["decision"] == "INVALIDATED"
    assert result["valid"] is True
    assert result["reason"] == "NO_RISK_ACTION"

    print("test_invalidated_has_no_risk_action: PASS")


def test_risk_failure_blocks_signal():
    result = validate_risk_signal(
        signal("BUY"),
        {"valid": False},
        {"valid": True},
        {"allowed": True},
    )

    assert result["decision"] == "WAIT"
    assert result["valid"] is False
    assert result["reason"] == "RISK_INVALID"

    print("test_risk_failure_blocks_signal: PASS")


def test_position_failure_blocks_signal():
    result = validate_risk_signal(
        signal("BUY"),
        {"valid": True},
        {"valid": False},
        {"allowed": True},
    )

    assert result["decision"] == "WAIT"
    assert result["reason"] == "POSITION_INVALID"

    print("test_position_failure_blocks_signal: PASS")


def test_guard_blocks_signal():
    result = validate_risk_signal(
        signal("BUY"),
        {"valid": True},
        {"valid": True},
        {"allowed": False},
    )

    assert result["decision"] == "WAIT"
    assert result["reason"] == "RISK_GUARD_BLOCKED"

    print("test_guard_blocks_signal: PASS")


def test_no_execution_keys():
    result = validate_risk_signal(
        signal("BUY"),
        {"valid": True},
        {"valid": True},
        {"allowed": True},
    )

    forbidden = {
        "order",
        "execute",
        "execution",
        "broker",
        "trade_id",
    }

    assert forbidden.isdisjoint(result.keys())

    print("test_no_execution_keys: PASS")


if __name__ == "__main__":
    test_buy_risk_validated()
    test_sell_risk_validated()
    test_wait_has_no_risk_action()
    test_invalidated_has_no_risk_action()
    test_risk_failure_blocks_signal()
    test_position_failure_blocks_signal()
    test_guard_blocks_signal()
    test_no_execution_keys()

    print("STEP 11A RISK VALIDATION TESTS: PASS")
