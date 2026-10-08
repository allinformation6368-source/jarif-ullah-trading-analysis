from analysis.unified_trade_plan import build_unified_trade_plan


def make_decision():
    return {
        "decision": "ENTRY_READY",
        "signal": "LONG",
    }


def make_risk():
    return {
        "status": "VALID",
        "signal": "LONG",
        "entry": 100,
        "stop_loss": 95,
        "take_profit": 110,
        "risk": 5,
        "reward": 10,
        "risk_reward": 2,
        "sl_source": "STRUCTURE",
    }


def make_sizing():
    return {
        "status": "VALID",
        "account_balance": 10000,
        "risk_percent": 1,
        "risk_amount": 100,
        "entry": 100,
        "stop_loss": 95,
        "price_risk": 5,
        "position_size": 20,
    }


def make_guard():
    return {
        "status": "APPROVED",
        "signal": "LONG",
        "entry": 100,
        "stop_loss": 95,
        "take_profit": 110,
        "risk": 5,
        "reward": 10,
        "risk_reward": 2,
    }


def test_unified_trade_plan_ready():
    result = build_unified_trade_plan(
        decision=make_decision(),
        risk=make_risk(),
        position_sizing=make_sizing(),
        risk_guard=make_guard(),
    )

    assert result["status"] == "READY"
    assert result["signal"] == "LONG"
    assert result["entry"] == 100
    assert result["stop_loss"] == 95
    assert result["take_profit"] == 110
    assert result["risk"] == 5
    assert result["reward"] == 10
    assert result["risk_reward"] == 2
    assert result["sl_source"] == "STRUCTURE"
    assert result["position_size"] == 20
    assert result["risk_amount"] == 100
    assert result["risk_guard"] == "APPROVED"


def test_unified_trade_plan_wait():
    result = build_unified_trade_plan(
        decision={"decision": "WAIT", "signal": None},
        risk=None,
    )

    assert result["status"] == "WAIT"


def test_unified_trade_plan_rejects_invalid_risk():
    result = build_unified_trade_plan(
        decision=make_decision(),
        risk={"status": "REJECTED"},
    )

    assert result["status"] == "REJECTED"
    assert result["reason"] == "Invalid risk"


def test_unified_trade_plan_rejects_risk_guard():
    result = build_unified_trade_plan(
        decision=make_decision(),
        risk=make_risk(),
        risk_guard={
            "status": "REJECTED",
            "reason": "Invalid risk",
        },
    )

    assert result["status"] == "REJECTED"
    assert result["reason"] == "Risk guard rejected trade"


def test_unified_trade_plan_rejects_invalid_position_sizing():
    result = build_unified_trade_plan(
        decision=make_decision(),
        risk=make_risk(),
        position_sizing={
            "status": "REJECTED",
            "reason": "Invalid position size",
        },
    )

    assert result["status"] == "REJECTED"
    assert result["reason"] == "Invalid position sizing"


if __name__ == "__main__":
    test_unified_trade_plan_ready()
    test_unified_trade_plan_wait()
    test_unified_trade_plan_rejects_invalid_risk()
    test_unified_trade_plan_rejects_risk_guard()
    test_unified_trade_plan_rejects_invalid_position_sizing()
    print("UNIFIED TRADE PLAN CONTRACT TEST: SUCCESS")
