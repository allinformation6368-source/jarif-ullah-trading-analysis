from analysis.execution_gateway import execute_order


def valid_order():
    return {
        "signal": "BUY",
        "entry": 100,
        "stop_loss": 95,
        "take_profit": 110,
        "risk_guard": "APPROVED",
    }


def test_paper_execution_contains_audit():
    result = execute_order(valid_order())

    assert result["status"] == "PAPER_ACCEPTED"
    assert "audit" in result
    assert result["audit"]["execution_status"] == "PAPER_ACCEPTED"
    assert result["audit"]["mode"] == "PAPER"
    assert result["audit"]["signal"] == "BUY"
    assert result["audit"]["entry"] == 100


def test_live_execution_contains_audit():
    result = execute_order(
        valid_order(),
        mode="LIVE",
    )

    assert result["status"] == "REJECTED"
    assert "audit" in result
    assert result["audit"]["execution_status"] == "REJECTED"
    assert result["audit"]["mode"] == "LIVE"
    assert result["audit"]["reason"] == "Live execution adapter is not enabled"


def test_invalid_order_contains_audit():
    result = execute_order({})

    assert result["status"] == "REJECTED"
    assert "audit" in result
    assert result["audit"]["execution_status"] == "REJECTED"


def test_invalid_execution_mode_contains_audit():
    result = execute_order(
        valid_order(),
        mode="INVALID",
    )

    assert result["status"] == "REJECTED"
    assert "audit" in result
    assert result["audit"]["execution_status"] == "REJECTED"
