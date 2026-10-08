from analysis.trade_decision import evaluate_trade_decision


def test_entry_ready_long():
    result = evaluate_trade_decision(
        {
            "signal": "LONG",
            "score": 60,
            "confidence": 80,
        }
    )

    assert result["decision"] == "ENTRY_READY"
    assert result["signal"] == "LONG"


def test_entry_ready_short():
    result = evaluate_trade_decision(
        {
            "signal": "SHORT",
            "score": -60,
            "confidence": 80,
        }
    )

    assert result["decision"] == "ENTRY_READY"
    assert result["signal"] == "SHORT"


def test_low_confidence_wait():
    result = evaluate_trade_decision(
        {
            "signal": "LONG",
            "score": 10,
            "confidence": 20,
        }
    )

    assert result["decision"] == "WAIT"


def test_wait_signal():
    result = evaluate_trade_decision(
        {
            "signal": "WAIT",
            "score": 1,
            "confidence": 10,
        }
    )

    assert result["decision"] == "WAIT"


print("TRADE DECISION TEST: SUCCESS")


def test_exact_threshold():
    result = evaluate_trade_decision(
        {
            "signal": "LONG",
            "score": 6,
            "confidence": 60,
        }
    )

    assert result["decision"] == "ENTRY_READY"


def test_below_threshold():
    result = evaluate_trade_decision(
        {
            "signal": "SHORT",
            "score": -6,
            "confidence": 59,
        }
    )

    assert result["decision"] == "WAIT"


def test_zero_confidence():
    result = evaluate_trade_decision(
        {
            "signal": "LONG",
            "score": 10,
            "confidence": 0,
        }
    )

    assert result["decision"] == "WAIT"


def test_unknown_signal():
    result = evaluate_trade_decision(
        {
            "signal": "UNKNOWN",
            "score": 100,
            "confidence": 100,
        }
    )

    assert result["decision"] == "WAIT"


print("TRADE DECISION EDGE CASES: SUCCESS")
