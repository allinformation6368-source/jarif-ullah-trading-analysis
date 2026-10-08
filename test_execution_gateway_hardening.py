import analysis.execution_gateway as gateway


def valid_order():
    return {
        "signal": "BUY",
        "entry": 100.0,
        "stop_loss": 95.0,
        "take_profit": 110.0,
    }


def test_validate_execution_order_rejects_non_dict():
    result = gateway.validate_execution_order(None)

    assert result["status"] == "REJECTED"
    assert result["reason"] == "Invalid order"


def test_validate_execution_order_rejects_missing_signal():
    order = valid_order()
    del order["signal"]

    result = gateway.validate_execution_order(order)

    assert result["status"] == "REJECTED"
    assert result["reason"] == "Missing order field: signal"


def test_validate_execution_order_rejects_missing_entry():
    order = valid_order()
    del order["entry"]

    result = gateway.validate_execution_order(order)

    assert result["status"] == "REJECTED"
    assert result["reason"] == "Missing order field: entry"


def test_validate_execution_order_rejects_missing_stop_loss():
    order = valid_order()
    del order["stop_loss"]

    result = gateway.validate_execution_order(order)

    assert result["status"] == "REJECTED"
    assert result["reason"] == "Missing order field: stop_loss"


def test_validate_execution_order_rejects_missing_take_profit():
    order = valid_order()
    del order["take_profit"]

    result = gateway.validate_execution_order(order)

    assert result["status"] == "REJECTED"
    assert result["reason"] == "Missing order field: take_profit"


def test_validate_execution_order_rejects_invalid_signal():
    order = valid_order()
    order["signal"] = "INVALID"

    result = gateway.validate_execution_order(order)

    assert result["status"] == "REJECTED"
    assert result["reason"] == "Invalid signal"


def test_execute_paper_order_rejects_invalid_order():
    result = gateway.execute_paper_order(
        order={"signal": "INVALID"},
    )

    assert result["status"] == "REJECTED"


def test_execute_paper_order_rejects_invalid_risk_config():
    result = gateway.execute_paper_order(
        order=valid_order(),
        account_balance=0,
        risk_percent=1.0,
    )

    assert result["status"] == "REJECTED"


def test_execute_live_order_never_executes():
    result = gateway.execute_live_order(valid_order())

    assert result["status"] == "REJECTED"
    assert result["mode"] == "LIVE"
    assert result["reason"] == "Live execution adapter is not enabled"


def test_execute_order_rejects_invalid_mode_and_creates_audit(monkeypatch):
    captured = []

    monkeypatch.setattr(
        gateway,
        "persist_execution_audit",
        lambda audit: captured.append(audit),
    )

    result = gateway.execute_order(
        order=valid_order(),
        mode="INVALID",
    )

    assert result["status"] == "REJECTED"
    assert result["audit"]["execution_status"] == "REJECTED"
    assert len(captured) == 1


def test_execute_order_live_mode_is_safely_rejected(monkeypatch):
    captured = []

    monkeypatch.setattr(
        gateway,
        "persist_execution_audit",
        lambda audit: captured.append(audit),
    )

    result = gateway.execute_order(
        order=valid_order(),
        mode="LIVE",
    )

    assert result["status"] == "REJECTED"
    assert result["mode"] == "LIVE"
    assert "adapter is not enabled" in result["reason"]
    assert len(captured) == 1
    assert captured[0]["execution_status"] == "REJECTED"
    assert captured[0]["mode"] == "LIVE"


def test_execute_order_paper_success_creates_audit(monkeypatch):
    captured = []

    monkeypatch.setattr(
        gateway,
        "persist_execution_audit",
        lambda audit: captured.append(audit),
    )

    result = gateway.execute_order(
        order=valid_order(),
        mode="PAPER",
        account_balance=10000,
        risk_percent=1.0,
        risk_reward=2.0,
    )

    assert result["status"] == "PAPER_ACCEPTED"
    assert result["mode"] == "PAPER"
    assert result["signal"] == "BUY"

    assert len(captured) == 1
    assert captured[0]["execution_status"] == "PAPER_ACCEPTED"
    assert captured[0]["mode"] == "PAPER"
    assert captured[0]["signal"] == "BUY"


def test_execute_order_audit_persistence_failure_does_not_change_execution_result(
    monkeypatch,
):
    def fail_persistence(audit):
        raise OSError("Synthetic audit storage failure")

    monkeypatch.setattr(
        gateway,
        "persist_execution_audit",
        fail_persistence,
    )

    try:
        result = gateway.execute_order(
            order=valid_order(),
            mode="PAPER",
        )
    except OSError as error:
        assert str(error) == "Synthetic audit storage failure"
    else:
        assert result["status"] == "PAPER_ACCEPTED"


def test_execution_audit_does_not_expose_unrelated_order_fields(monkeypatch):
    captured = []

    monkeypatch.setattr(
        gateway,
        "persist_execution_audit",
        lambda audit: captured.append(audit),
    )

    order = valid_order()
    order["secret_internal_field"] = "DO_NOT_LOG"

    result = gateway.execute_order(
        order=order,
        mode="PAPER",
    )

    assert result["status"] == "PAPER_ACCEPTED"
    assert len(captured) == 1
    assert "secret_internal_field" not in captured[0]
