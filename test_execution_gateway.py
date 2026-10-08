from analysis.execution_gateway import (
    validate_execution_order,
    execute_paper_order,
    execute_live_order,
    execute_order,
)


def valid_order():
    return {
        "signal": "BUY",
        "entry": 100,
        "stop_loss": 95,
        "take_profit": 110,
        "risk_guard": "APPROVED",
    }


def test_validate_execution_order():
    result = validate_execution_order(valid_order())
    assert result["status"] == "VALID"


def test_validate_execution_order_rejects_missing_field():
    order = valid_order()
    del order["stop_loss"]

    result = validate_execution_order(order)

    assert result["status"] == "REJECTED"


def test_validate_execution_order_rejects_invalid_signal():
    order = valid_order()
    order["signal"] = "HOLD"

    result = validate_execution_order(order)

    assert result["status"] == "REJECTED"


def test_execute_paper_order():
    result = execute_paper_order(valid_order())

    assert result["status"] == "PAPER_ACCEPTED"
    assert result["mode"] == "PAPER"
    assert result["signal"] == "BUY"
    assert result["risk_percent"] == 1.0


def test_execute_paper_order_accepts_custom_risk():
    result = execute_paper_order(
        valid_order(),
        account_balance=25000,
        risk_percent=2,
        risk_reward=3,
    )

    assert result["status"] == "PAPER_ACCEPTED"
    assert result["account_balance"] == 25000
    assert result["risk_percent"] == 2
    assert result["risk_reward"] == 3


def test_execute_paper_order_rejects_invalid_balance():
    result = execute_paper_order(
        valid_order(),
        account_balance=0,
    )

    assert result["status"] == "REJECTED"


def test_execute_paper_order_rejects_excessive_risk():
    result = execute_paper_order(
        valid_order(),
        risk_percent=10,
    )

    assert result["status"] == "REJECTED"


def test_execute_live_order_is_blocked():
    result = execute_live_order(valid_order())

    assert result["status"] == "REJECTED"
    assert result["mode"] == "LIVE"


def test_execute_order_defaults_to_paper():
    result = execute_order(valid_order())

    assert result["status"] == "PAPER_ACCEPTED"
    assert result["mode"] == "PAPER"


def test_execute_order_live_is_blocked():
    result = execute_order(
        valid_order(),
        mode="LIVE",
    )

    assert result["status"] == "REJECTED"


def test_execute_order_invalid_mode():
    result = execute_order(
        valid_order(),
        mode="UNKNOWN",
    )

    assert result["status"] == "REJECTED"


def test_execute_order_applies_risk_config():
    result = execute_order(
        valid_order(),
        account_balance=50000,
        risk_percent=1.5,
        risk_reward=2.5,
    )

    assert result["status"] == "PAPER_ACCEPTED"
    assert result["account_balance"] == 50000
    assert result["risk_percent"] == 1.5
    assert result["risk_reward"] == 2.5
