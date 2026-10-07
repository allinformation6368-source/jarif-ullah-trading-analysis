from analysis.mtf_confluence import calculate_mtf_confluence


results = {
    "5m": {
        "confluence": {
            "signal": "LONG",
            "score": 6,
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
            "signal": "SHORT",
            "score": -8,
        }
    },
}


try:
    result = calculate_mtf_confluence(results)

    print("WEIGHTED CONFLICT TEST: SUCCESS")
    print("Signal:", result["signal"])
    print("Score:", result["score"])
    print("Confidence:", result["confidence"])
    print("Reasons:", result["reasons"])

except Exception as e:
    print("WEIGHTED CONFLICT TEST: FAILED")
    print(type(e).__name__, ":", e)
