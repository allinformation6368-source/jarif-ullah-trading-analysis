from config.validation import validate_runtime_config


def test_valid_runtime_config():
    result = validate_runtime_config(
        api_key="test-key",
        account_balance=10000,
        risk_percent=1.0,
    )

    assert result["status"] == "VALID"
    assert result["account_balance"] == 10000.0
    assert result["risk_percent"] == 1.0
    assert result["api_key_configured"] is True


def test_missing_api_key_is_rejected():
    result = validate_runtime_config(
        api_key=None,
        account_balance=10000,
        risk_percent=1.0,
    )

    assert result["status"] == "REJECTED"
    assert result["reason"] == "Missing API key"


def test_blank_api_key_is_rejected():
    result = validate_runtime_config(
        api_key="   ",
        account_balance=10000,
        risk_percent=1.0,
    )

    assert result["status"] == "REJECTED"


def test_invalid_account_balance_is_rejected():
    result = validate_runtime_config(
        api_key="test-key",
        account_balance=0,
        risk_percent=1.0,
    )

    assert result["status"] == "REJECTED"
    assert result["reason"] == "Invalid account balance"


def test_non_numeric_account_balance_is_rejected():
    result = validate_runtime_config(
        api_key="test-key",
        account_balance="10000",
        risk_percent=1.0,
    )

    assert result["status"] == "REJECTED"


def test_invalid_risk_percent_is_rejected():
    result = validate_runtime_config(
        api_key="test-key",
        account_balance=10000,
        risk_percent=0,
    )

    assert result["status"] == "REJECTED"
    assert result["reason"] == "Invalid risk percent"


def test_risk_percent_over_100_is_rejected():
    result = validate_runtime_config(
        api_key="test-key",
        account_balance=10000,
        risk_percent=101,
    )

    assert result["status"] == "REJECTED"
    assert result["reason"] == "Risk percent exceeds 100"


def test_non_numeric_risk_percent_is_rejected():
    result = validate_runtime_config(
        api_key="test-key",
        account_balance=10000,
        risk_percent="1",
    )

    assert result["status"] == "REJECTED"


def test_api_key_is_not_returned():
    result = validate_runtime_config(
        api_key="SUPER_SECRET_TEST_KEY",
        account_balance=10000,
        risk_percent=1.0,
    )

    assert "SUPER_SECRET_TEST_KEY" not in str(result)
    assert "api_key" not in result
