from analysis.mtf_confluence import calculate_mtf_confluence


results = {
    "5m": {
        "confluence": {
            "signal": "LONG",
            "score": 10,
        }
    },
    "15m": {
        "confluence": {
            "signal": "LONG",
            "score": 10,
        }
    },
    "1h": {
        "confluence": {
            "signal": "SHORT",
            "score": -10,
        }
    },
}


result = calculate_mtf_confluence(results)

print("MTF HTF GATE TEST")
print("Signal:", result["signal"])
print("Score:", result["score"])
print("Confidence:", result["confidence"])
print("Reasons:", result["reasons"])

assert result["signal"] == "WAIT"

print("MTF HTF GATE TEST: SUCCESS")
