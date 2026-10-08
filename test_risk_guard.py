from analysis.risk_guard import validate_trade_risk


def make_valid_risk():
    return {
        "status": "VALID",
        "signal": "LONG",
        "entry": 100,
        "stop_loss": 95,
        "take_profit": 110,
        "risk": 5,
        "reward": 10,
        "risk_reward": 2,
    }


def make_valid_sizing():
    return {
        "status": "VALID",
        "account_balance": 10000,
        "risk_percent": 1,
        "risk_amount": 100,
        "entry": 100,
        "stop_loss": 95,
        "position_size": 20,
    }


def test_valid_risk_is_approved():
    result = validate_trade_risk(make_valid_risk())

    assert result["status"] == "APPROVED"
    assert result["signal"] == "LONG"
    assert result["risk_reward"] == 2


def test_valid_risk_and_position_sizing_are_approved():
    result = validate_trade_risk(
        make_valid_risk(),
        make_valid_sizing(),
    )

    assert result["status"] == "APPROVED"
    assert result["entry"] == 100
    assert result["stop_loss"] == 95


def test_invalid_risk_is_rejected():
    risk = make_valid_risk()
    risk["status"] = "REJECTED"

    result = validate_trade_risk(risk)

    assert result["status"] == "REJECTED"


def test_invalid_position_sizing_is_rejected():
    sizing = make_valid_sizing()
    sizing["status"] = "REJECTED"

    result = validate_trade_risk(
        make_valid_risk(),
        sizing,
    )

    assert result["status"] == "REJECTED"


def test_zero_position_size_is_rejected():
    sizing = make_valid_sizing()
    sizing["position_size"] = 0

    result = validate_trade_risk(
        make_valid_risk(),
        sizing,
    )

    assert result["status"] == "REJECTED"


def test_missing_risk_field_is_rejected():
    risk = make_valid_risk()
    del risk["stop_loss"]

    result = validate_trade_risk(risk)

    assert result["status"] == "REJECTED"


if __name__ == "__main__":
    test_valid_risk_is_approved()
    test_valid_risk_and_position_sizing_are_approved()
    test_invalid_risk_is_rejected()
    test_invalid_position_sizing_is_rejected()
    test_zero_position_size_is_rejected()
    test_missing_risk_field_is_rejected()

    print("RISK GUARD CONTRACT TEST: SUCCESS")
