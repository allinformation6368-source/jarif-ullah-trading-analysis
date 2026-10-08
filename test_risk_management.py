from analysis.risk_management import calculate_risk


def test_valid_long():
    result = calculate_risk(
        signal="LONG",
        entry=100,
        stop_loss=95,
        take_profit=110,
    )

    assert result["status"] == "VALID"
    assert result["signal"] == "LONG"
    assert result["entry"] == 100
    assert result["stop_loss"] == 95
    assert result["take_profit"] == 110
    assert result["risk"] == 5
    assert result["reward"] == 10
    assert result["risk_reward"] == 2


def test_valid_short():
    result = calculate_risk(
        signal="SHORT",
        entry=100,
        stop_loss=105,
        take_profit=90,
    )

    assert result["status"] == "VALID"
    assert result["signal"] == "SHORT"
    assert result["risk"] == 5
    assert result["reward"] == 10
    assert result["risk_reward"] == 2


def test_invalid_long_levels():
    result = calculate_risk(
        signal="LONG",
        entry=100,
        stop_loss=105,
        take_profit=110,
    )

    assert result["status"] == "REJECTED"


def test_invalid_short_levels():
    result = calculate_risk(
        signal="SHORT",
        entry=100,
        stop_loss=95,
        take_profit=90,
    )

    assert result["status"] == "REJECTED"


def test_invalid_signal():
    result = calculate_risk(
        signal="WAIT",
        entry=100,
        stop_loss=95,
        take_profit=110,
    )

    assert result["status"] == "REJECTED"


def test_zero_risk():
    result = calculate_risk(
        signal="LONG",
        entry=100,
        stop_loss=100,
        take_profit=110,
    )

    assert result["status"] == "REJECTED"


if __name__ == "__main__":
    test_valid_long()
    test_valid_short()
    test_invalid_long_levels()
    test_invalid_short_levels()
    test_invalid_signal()
    test_zero_risk()

    print("RISK MANAGEMENT CONTRACT TEST: SUCCESS")
