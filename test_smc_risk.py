from analysis.risk_management import calculate_smc_risk


def test_long_from_structure():
    result = calculate_smc_risk(
        signal="LONG",
        entry=100,
        structure_level=95,
        risk_reward=2,
    )

    assert result["status"] == "VALID"
    assert result["signal"] == "LONG"
    assert result["entry"] == 100
    assert result["stop_loss"] == 95
    assert result["take_profit"] == 110
    assert result["risk"] == 5
    assert result["reward"] == 10
    assert result["risk_reward"] == 2


def test_short_from_structure():
    result = calculate_smc_risk(
        signal="SHORT",
        entry=100,
        structure_level=105,
        risk_reward=2,
    )

    assert result["status"] == "VALID"
    assert result["signal"] == "SHORT"
    assert result["entry"] == 100
    assert result["stop_loss"] == 105
    assert result["take_profit"] == 90
    assert result["risk"] == 5
    assert result["reward"] == 10
    assert result["risk_reward"] == 2


def test_invalid_long_structure():
    result = calculate_smc_risk(
        signal="LONG",
        entry=100,
        structure_level=105,
        risk_reward=2,
    )

    assert result["status"] == "REJECTED"


def test_invalid_short_structure():
    result = calculate_smc_risk(
        signal="SHORT",
        entry=100,
        structure_level=95,
        risk_reward=2,
    )

    assert result["status"] == "REJECTED"


def test_invalid_signal():
    result = calculate_smc_risk(
        signal="WAIT",
        entry=100,
        structure_level=95,
        risk_reward=2,
    )

    assert result["status"] == "REJECTED"


def test_invalid_risk_reward():
    result = calculate_smc_risk(
        signal="LONG",
        entry=100,
        structure_level=95,
        risk_reward=1.5,
    )

    assert result["status"] == "REJECTED"


if __name__ == "__main__":
    test_long_from_structure()
    test_short_from_structure()
    test_invalid_long_structure()
    test_invalid_short_structure()
    test_invalid_signal()
    test_invalid_risk_reward()

    print("SMC RISK CONTRACT TEST: SUCCESS")
