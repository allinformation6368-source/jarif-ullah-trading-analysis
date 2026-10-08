from analysis.mtf_engine import analyze_multi_timeframe
from analysis.trade_decision import evaluate_trade_decision


def test_mtf_long_entry_ready():
    results = {
        "5m": {
            "confluence": {
                "signal": "LONG",
                "score": 8,
                "confidence": 80,
            }
        },
        "15m": {
            "confluence": {
                "signal": "LONG",
                "score": 8,
                "confidence": 80,
            }
        },
        "1h": {
            "confluence": {
                "signal": "LONG",
                "score": 8,
                "confidence": 80,
            }
        },
    }

    from analysis.mtf_confluence import calculate_mtf_confluence

    mtf = calculate_mtf_confluence(results)

    decision = evaluate_trade_decision(mtf)

    assert mtf["signal"] == "LONG"
    assert mtf["confidence"] >= 60
    assert decision["decision"] == "ENTRY_READY"
    assert decision["signal"] == "LONG"


def test_mtf_conflict_wait():
    results = {
        "5m": {
            "confluence": {
                "signal": "LONG",
                "score": 6,
                "confidence": 60,
            }
        },
        "15m": {
            "confluence": {
                "signal": "LONG",
                "score": 6,
                "confidence": 60,
            }
        },
        "1h": {
            "confluence": {
                "signal": "SHORT",
                "score": -8,
                "confidence": 80,
            }
        },
    }

    from analysis.mtf_confluence import calculate_mtf_confluence

    mtf = calculate_mtf_confluence(results)

    decision = evaluate_trade_decision(mtf)

    assert mtf["signal"] == "SHORT"
    assert mtf["confidence"] == 10
    assert decision["decision"] == "WAIT"


print("MTF TRADE DECISION TEST: SUCCESS")
