from analysis.mtf_confluence import calculate_mtf_confluence


results = {
    "5m": {
        "confluence": {
            "signal": "LONG",
            "score": 2,
        }
    },
    "15m": {
        "confluence": {
            "signal": "SHORT",
            "score": -2,
        }
    },
    "1h": {
        "confluence": {
            "signal": "LONG",
            "score": 1,
        }
    },
}


try:
    result = calculate_mtf_confluence(results)

    print("WEIGHTED WAIT TEST: SUCCESS")
    print("Signal:", result["signal"])
    print("Score:", result["score"])
    print("Confidence:", result["confidence"])
    print("Reasons:", result["reasons"])

except Exception as e:
    print("WEIGHTED WAIT TEST: FAILED")
    print(type(e).__name__, ":", e)
