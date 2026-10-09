from terminal_ui.scanner_status import (
    build_scanner_status,
    format_scanner_status,
)


def test_active_status():
    result = build_scanner_status(
        scanner_status="ACTIVE",
        current_pair="BTC/USD",
        next_pair="ETH/USD",
        signal="BUY",
        quality="HIGH",
        confidence=100,
        setup_state="ACTIVE",
        credits_used=120,
        credits_remaining=630,
    )

    assert result["scanner_status"] == "ACTIVE"
    assert result["current_pair"] == "BTC/USD"
    assert result["next_pair"] == "ETH/USD"
    assert result["signal"] == "BUY"
    assert result["quality"] == "HIGH"
    assert result["confidence"] == 100
    assert result["credits_used"] == 120
    assert result["planned_budget"] == 750
    assert result["safety_reserve"] == 50
    assert result["live_execution"] is False

    print("test_active_status: PASS")


def test_paused_status():
    result = build_scanner_status(
        scanner_status="PAUSED",
        current_pair="EUR/USD",
        signal="WAIT",
    )

    assert result["scanner_status"] == "PAUSED"
    assert result["signal"] == "WAIT"
    assert result["live_execution"] is False

    print("test_paused_status: PASS")


def test_budget_limit_status():
    result = build_scanner_status(
        scanner_status="BUDGET_LIMIT",
        credits_used=750,
        credits_remaining=50,
    )

    assert result["scanner_status"] == "BUDGET_LIMIT"
    assert result["credits_used"] == 750
    assert result["credits_remaining"] == 50
    assert result["safety_reserve"] == 50

    print("test_budget_limit_status: PASS")


def test_confidence_clamped():
    high = build_scanner_status(
        scanner_status="ACTIVE",
        confidence=999,
    )

    low = build_scanner_status(
        scanner_status="ACTIVE",
        confidence=-50,
    )

    assert high["confidence"] == 100
    assert low["confidence"] == 0

    print("test_confidence_clamped: PASS")


def test_invalid_status_is_safe():
    result = build_scanner_status(
        scanner_status="UNKNOWN",
    )

    assert result["scanner_status"] == "PAUSED"

    print("test_invalid_status_is_safe: PASS")


def test_formatted_output():
    result = build_scanner_status(
        scanner_status="ACTIVE",
        current_pair="BTC/USD",
        next_pair="ETH/USD",
        signal="BUY",
        quality="HIGH",
        confidence=95,
        setup_state="ACTIVE",
        credits_used=100,
        credits_remaining=650,
    )

    output = format_scanner_status(result)

    assert "SCANNER: ACTIVE" in output
    assert "PAIR: BTC/USD" in output
    assert "NEXT: ETH/USD" in output
    assert "SIGNAL: BUY" in output
    assert "QUALITY: HIGH" in output
    assert "CONFIDENCE: 95/100" in output
    assert "CREDITS: 100/750" in output
    assert "reserve 50" in output
    assert "LIVE EXECUTION: OFF" in output

    print("test_formatted_output: PASS")


def test_no_execution_controls():
    result = build_scanner_status(
        scanner_status="ACTIVE",
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

    print("test_no_execution_controls: PASS")


if __name__ == "__main__":
    test_active_status()
    test_paused_status()
    test_budget_limit_status()
    test_confidence_clamped()
    test_invalid_status_is_safe()
    test_formatted_output()
    test_no_execution_controls()

    print("STEP 13A TUI STATUS TESTS: PASS")
