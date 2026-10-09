from analysis.scanner.setup_lifecycle import evaluate_setup_lifecycle


def test_new_setup_becomes_active():
    result = evaluate_setup_lifecycle(
        setup_id="BTC/USD|BUY",
        decision="BUY",
        candle_id="btc-100",
        now=1000,
    )

    assert result["state"] == "ACTIVE"
    assert result["active"] is True
    assert result["invalidated"] is False

    print("test_new_setup_becomes_active: PASS")


def test_active_setup_persists():
    result = evaluate_setup_lifecycle(
        setup_id="BTC/USD|BUY",
        decision="BUY",
        candle_id="btc-101",
        now=1100,
        previous_state="ACTIVE",
    )

    assert result["state"] == "ACTIVE"
    assert result["reason"] == "SETUP_STILL_ACTIVE"

    print("test_active_setup_persists: PASS")


def test_invalidated_setup():
    result = evaluate_setup_lifecycle(
        setup_id="BTC/USD|BUY",
        decision="INVALIDATED",
        candle_id="btc-102",
        now=1200,
        previous_state="ACTIVE",
    )

    assert result["state"] == "INVALIDATED"
    assert result["invalidated"] is True
    assert result["active"] is False

    print("test_invalidated_setup: PASS")


def test_expired_setup():
    result = evaluate_setup_lifecycle(
        setup_id="ETH/USD|SELL",
        decision="SELL",
        candle_id="eth-200",
        now=2000,
        expires_at=1900,
        previous_state="ACTIVE",
    )

    assert result["state"] == "EXPIRED"
    assert result["expired"] is True
    assert result["active"] is False

    print("test_expired_setup: PASS")


def test_expiry_boundary():
    result = evaluate_setup_lifecycle(
        setup_id="EUR/USD|BUY",
        decision="BUY",
        candle_id="eur-300",
        now=3000,
        expires_at=3000,
        previous_state="ACTIVE",
    )

    assert result["state"] == "EXPIRED"

    print("test_expiry_boundary: PASS")


def test_wait_does_not_create_new_entry():
    result = evaluate_setup_lifecycle(
        setup_id="GBP/USD|BUY",
        decision="WAIT",
        candle_id="gbp-400",
        now=4000,
        previous_state="NEW",
    )

    assert result["state"] == "ACTIVE"
    assert result["active"] is True
    assert result["decision"] == "WAIT"

    print("test_wait_does_not_create_new_entry: PASS")


def test_invalid_previous_state_is_safe():
    result = evaluate_setup_lifecycle(
        setup_id="USD/JPY|SELL",
        decision="SELL",
        candle_id="jpy-500",
        now=5000,
        previous_state="UNKNOWN_STATE",
    )

    assert result["state"] == "ACTIVE"

    print("test_invalid_previous_state_is_safe: PASS")


def test_no_execution_keys():
    result = evaluate_setup_lifecycle(
        setup_id="USD/CAD|BUY",
        decision="BUY",
        candle_id="cad-600",
        now=6000,
    )

    forbidden = {
        "order",
        "execute",
        "execution",
        "broker",
        "trade_id",
        "position",
    }

    assert forbidden.isdisjoint(result.keys())

    print("test_no_execution_keys: PASS")


if __name__ == "__main__":
    test_new_setup_becomes_active()
    test_active_setup_persists()
    test_invalidated_setup()
    test_expired_setup()
    test_expiry_boundary()
    test_wait_does_not_create_new_entry()
    test_invalid_previous_state_is_safe()
    test_no_execution_keys()

    print("STEP 12C SETUP LIFECYCLE TESTS: PASS")
