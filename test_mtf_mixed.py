from analysis.mtf_confluence import calculate_mtf_confluence


results = {
    "5m": {
        "confluence": {
            "signal": "SHORT",
            "score": -8,
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
            "score": 6,
        }
    },
}


try:
    result = calculate_mtf_confluence(results)

    print("MIXED MTF TEST: SUCCESS")
    print("Signal:", result["signal"])
    print("Score:", result["score"])
    print("Confidence:", result["confidence"])
    print("Reasons:", result["reasons"])

except Exception as e:
    print("MIXED MTF TEST: FAILED")
    print(type(e).__name__, ":", e)
