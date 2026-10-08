from config.risk import (
    DEFAULT_ACCOUNT_BALANCE,
    DEFAULT_RISK_PERCENT,
    DEFAULT_RISK_REWARD,
    DEFAULT_EXECUTION_MODE,
    MIN_RISK_PERCENT,
    MAX_RISK_PERCENT,
    validate_risk_config,
    validate_execution_mode,
)


def test_default_risk_config():
    result = validate_risk_config()

    assert result["status"] == "VALID"
    assert result["account_balance"] == DEFAULT_ACCOUNT_BALANCE
    assert result["risk_percent"] == DEFAULT_RISK_PERCENT
    assert result["risk_reward"] == DEFAULT_RISK_REWARD


def test_valid_custom_risk_config():
    result = validate_risk_config(
        account_balance=25000,
        risk_percent=2,
        risk_reward=3,
    )

    assert result["status"] == "VALID"
    assert result["account_balance"] == 25000
    assert result["risk_percent"] == 2
    assert result["risk_reward"] == 3


def test_invalid_account_balance():
    result = validate_risk_config(
        account_balance=0,
        risk_percent=1,
    )

    assert result["status"] == "REJECTED"


def test_risk_percent_below_minimum():
    result = validate_risk_config(
        account_balance=10000,
        risk_percent=MIN_RISK_PERCENT - 0.01,
    )

    assert result["status"] == "REJECTED"


def test_risk_percent_above_maximum():
    result = validate_risk_config(
        account_balance=10000,
        risk_percent=MAX_RISK_PERCENT + 0.01,
    )

    assert result["status"] == "REJECTED"


def test_invalid_risk_reward():
    result = validate_risk_config(
        account_balance=10000,
        risk_percent=1,
        risk_reward=0,
    )

    assert result["status"] == "REJECTED"


def test_default_execution_mode_is_paper():
    result = validate_execution_mode()

    assert result["status"] == "VALID"
    assert result["mode"] == DEFAULT_EXECUTION_MODE
    assert DEFAULT_EXECUTION_MODE == "PAPER"


def test_paper_execution_mode():
    result = validate_execution_mode("PAPER")

    assert result["status"] == "VALID"
    assert result["mode"] == "PAPER"


def test_live_execution_is_blocked():
    result = validate_execution_mode("LIVE")

    assert result["status"] == "REJECTED"


def test_invalid_execution_mode():
    result = validate_execution_mode("UNKNOWN")

    assert result["status"] == "REJECTED"
