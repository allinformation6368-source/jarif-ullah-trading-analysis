from analysis.mtf_engine import analyze_multi_timeframe


timeframes = {
    "5m": [],
    "15m": [],
    "1h": [],
}


try:
    result = analyze_multi_timeframe(timeframes)

    print("MTF ENGINE TEST: SUCCESS")
    print("Result type:", type(result).__name__)
    print("Timeframes:", list(result["timeframes"].keys()))

    for timeframe, analysis in result["timeframes"].items():
        print(
            timeframe,
            "->",
            analysis["confluence"]["signal"]
        )

    print("FINAL SIGNAL:", result["confluence"]["signal"])
    print("FINAL SCORE:", result["confluence"]["score"])
    print("FINAL CONFIDENCE:", result["confluence"]["confidence"])

except Exception as e:
    print("MTF ENGINE TEST: FAILED")
    print(type(e).__name__, ":", e)
