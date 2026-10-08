from analysis.position_sizing import calculate_position_size


def test_long_position_size():
    result = calculate_position_size(
        account_balance=10000,
        risk_percent=1,
        entry=100,
        stop_loss=95,
    )

    assert result["status"] == "VALID"
    assert result["risk_amount"] == 100
    assert result["price_risk"] == 5
    assert result["position_size"] == 20


def test_short_position_size():
    result = calculate_position_size(
        account_balance=10000,
        risk_percent=1,
        entry=100,
        stop_loss=105,
    )

    assert result["status"] == "VALID"
    assert result["risk_amount"] == 100
    assert result["price_risk"] == 5
    assert result["position_size"] == 20


def test_invalid_balance():
    result = calculate_position_size(
        account_balance=0,
        risk_percent=1,
        entry=100,
        stop_loss=95,
    )

    assert result["status"] == "REJECTED"


def test_negative_balance():
    result = calculate_position_size(
        account_balance=-1000,
        risk_percent=1,
        entry=100,
        stop_loss=95,
    )

    assert result["status"] == "REJECTED"


def test_invalid_risk_percent():
    result = calculate_position_size(
        account_balance=10000,
        risk_percent=0,
        entry=100,
        stop_loss=95,
    )

    assert result["status"] == "REJECTED"


def test_negative_risk_percent():
    result = calculate_position_size(
        account_balance=10000,
        risk_percent=-1,
        entry=100,
        stop_loss=95,
    )

    assert result["status"] == "REJECTED"


def test_invalid_entry():
    result = calculate_position_size(
        account_balance=10000,
        risk_percent=1,
        entry=0,
        stop_loss=95,
    )

    assert result["status"] == "REJECTED"


def test_invalid_stop_loss():
    result = calculate_position_size(
        account_balance=10000,
        risk_percent=1,
        entry=100,
        stop_loss=0,
    )

    assert result["status"] == "REJECTED"


def test_equal_entry_stop():
    result = calculate_position_size(
        account_balance=10000,
        risk_percent=1,
        entry=100,
        stop_loss=100,
    )

    assert result["status"] == "REJECTED"


if __name__ == "__main__":
    test_long_position_size()
    test_short_position_size()
    test_invalid_balance()
    test_negative_balance()
    test_invalid_risk_percent()
    test_negative_risk_percent()
    test_invalid_entry()
    test_invalid_stop_loss()
    test_equal_entry_stop()

    print("POSITION SIZING VALIDATION CONTRACT TEST: SUCCESS")
