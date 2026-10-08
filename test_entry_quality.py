from analysis.entry_quality import evaluate_entry_quality


def test_entry_ready():
    confluence = {
        "signal": "LONG",
        "score": 36,
        "confidence": 60,
    }

    decision = {
        "decision": "ENTRY_READY",
        "signal": "LONG",
        "confidence": 60,
    }

    result = evaluate_entry_quality(
        confluence,
        decision,
    )

    assert result["status"] == "VALID"
    assert result["signal"] == "LONG"


def test_wait_decision():
    confluence = {
        "signal": "LONG",
        "score": 22,
        "confidence": 37,
    }

    decision = {
        "decision": "WAIT",
        "signal": "LONG",
        "confidence": 37,
    }

    result = evaluate_entry_quality(
        confluence,
        decision,
    )

    assert result["status"] == "REJECTED"


def test_signal_mismatch():
    confluence = {
        "signal": "LONG",
        "score": 36,
        "confidence": 60,
    }

    decision = {
        "decision": "ENTRY_READY",
        "signal": "SHORT",
        "confidence": 60,
    }

    result = evaluate_entry_quality(
        confluence,
        decision,
    )

    assert result["status"] == "REJECTED"


def test_wait_signal():
    confluence = {
        "signal": "WAIT",
        "score": 0,
        "confidence": 0,
    }

    decision = {
        "decision": "WAIT",
        "signal": "WAIT",
        "confidence": 0,
    }

    result = evaluate_entry_quality(
        confluence,
        decision,
    )

    assert result["status"] == "REJECTED"


if __name__ == "__main__":
    test_entry_ready()
    test_wait_decision()
    test_signal_mismatch()
    test_wait_signal()

    print("ENTRY QUALITY TEST: SUCCESS")
