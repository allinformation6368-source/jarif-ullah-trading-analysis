from analysis.unified_engine import analyze_timeframe

candles = []

try:
    result = analyze_timeframe(candles)

    print("ENGINE TEST: SUCCESS")
    print("Result type:", type(result).__name__)
    print("Keys:", list(result.keys()))

except Exception as e:
    print("ENGINE TEST: FAILED")
    print(type(e).__name__, ":", e)
