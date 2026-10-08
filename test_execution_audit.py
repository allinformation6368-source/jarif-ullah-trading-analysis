from analysis.execution_audit import (
    create_execution_audit,
    is_execution_successful,
)


def valid_order():
    return {
        "signal": "BUY",
        "entry": 100,
        "stop_loss": 95,
        "take_profit": 110,
    }


def test_create_execution_audit_for_paper_order():
    result = {
        "status": "PAPER_ACCEPTED",
        "mode": "PAPER",
        "account_balance": 10000,
        "risk_percent": 1,
        "risk_reward": 2,
    }

    audit = create_execution_audit(
        result=result,
        order=valid_order(),
    )

    assert audit["execution_status"] == "PAPER_ACCEPTED"
    assert audit["mode"] == "PAPER"
    assert audit["signal"] == "BUY"
    assert audit["entry"] == 100
    assert audit["stop_loss"] == 95
    assert audit["take_profit"] == 110
    assert audit["account_balance"] == 10000
    assert audit["risk_percent"] == 1
    assert audit["risk_reward"] == 2
    assert audit["timestamp"]


def test_create_execution_audit_for_rejection():
    result = {
        "status": "REJECTED",
        "mode": "LIVE",
        "reason": "Live execution adapter is not enabled",
    }

    audit = create_execution_audit(
        result=result,
        order=valid_order(),
    )

    assert audit["execution_status"] == "REJECTED"
    assert audit["mode"] == "LIVE"
    assert audit["reason"] == "Live execution adapter is not enabled"


def test_audit_can_use_result_signal():
    result = {
        "status": "PAPER_ACCEPTED",
        "mode": "PAPER",
        "signal": "SELL",
        "entry": 200,
        "stop_loss": 205,
        "take_profit": 190,
    }

    audit = create_execution_audit(result)

    assert audit["signal"] == "SELL"
    assert audit["entry"] == 200
    assert audit["stop_loss"] == 205
    assert audit["take_profit"] == 190


def test_invalid_result_is_rejected():
    audit = create_execution_audit(None)

    assert audit["status"] == "REJECTED"


def test_invalid_order_is_rejected():
    audit = create_execution_audit(
        result={"status": "PAPER_ACCEPTED"},
        order=[],
    )

    assert audit["status"] == "REJECTED"


def test_successful_paper_execution():
    audit = create_execution_audit(
        {
            "status": "PAPER_ACCEPTED",
            "mode": "PAPER",
        },
        valid_order(),
    )

    assert is_execution_successful(audit) is True


def test_rejected_execution_is_not_successful():
    audit = create_execution_audit(
        {
            "status": "REJECTED",
            "mode": "LIVE",
            "reason": "Blocked",
        },
        valid_order(),
    )

    assert is_execution_successful(audit) is False


def test_invalid_audit_is_not_successful():
    assert is_execution_successful(None) is False
