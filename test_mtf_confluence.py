from analysis.mtf_confluence import calculate_mtf_confluence


results = {
    "5m": {
        "confluence": {
            "signal": "WAIT",
            "score": 0,
        }
    },
    "15m": {
        "confluence": {
            "signal": "LONG",
            "score": 6,
        }
    },
    "1h": {
        "confluence": {
            "signal": "LONG",
            "score": 8,
        }
    },
}


try:
    result = calculate_mtf_confluence(results)

    print("MTF CONFLUENCE TEST: SUCCESS")
    print("Signal:", result["signal"])
    print("Score:", result["score"])
    print("Confidence:", result["confidence"])
    print("Reasons:", result["reasons"])

except Exception as e:
    print("MTF CONFLUENCE TEST: FAILED")
    print(type(e).__name__, ":", e)
