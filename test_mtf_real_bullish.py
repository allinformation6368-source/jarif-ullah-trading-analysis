from analysis.mtf_engine import analyze_multi_timeframe


candles = [
    {"datetime": "2026-10-07T09:15:00", "open": 100, "high": 103, "low": 99, "close": 101},
    {"datetime": "2026-10-07T09:20:00", "open": 101, "high": 105, "low": 99, "close": 103},
    {"datetime": "2026-10-07T09:25:00", "open": 103, "high": 106, "low": 97, "close": 100},
    {"datetime": "2026-10-07T09:30:00", "open": 100, "high": 104, "low": 100, "close": 102},
    {"datetime": "2026-10-07T09:35:00", "open": 102, "high": 107, "low": 101, "close": 105},
    {"datetime": "2026-10-07T09:40:00", "open": 105, "high": 106, "low": 97, "close": 103},
    {"datetime": "2026-10-07T09:45:00", "open": 103, "high": 109, "low": 102, "close": 108},
    {"datetime": "2026-10-07T09:50:00", "open": 108, "high": 108, "low": 103, "close": 104},
    {"datetime": "2026-10-07T09:55:00", "open": 104, "high": 106, "low": 95, "close": 103},
    {"datetime": "2026-10-07T10:00:00", "open": 103, "high": 112, "low": 102, "close": 111},
    {"datetime": "2026-10-07T10:05:00", "open": 111, "high": 115, "low": 110, "close": 114},
    {"datetime": "2026-10-07T10:10:00", "open": 114, "high": 117, "low": 112, "close": 116},
    {"datetime": "2026-10-07T10:15:00", "open": 116, "high": 117, "low": 108, "close": 110},
    {"datetime": "2026-10-07T10:20:00", "open": 110, "high": 112, "low": 96, "close": 100},
]


timeframes = {
    "5m": candles,
    "15m": candles,
    "1h": candles,
}


result = analyze_multi_timeframe(timeframes)

print("REAL MTF BULLISH TEST")

for timeframe, analysis in result["timeframes"].items():
    confluence = analysis["confluence"]
    print(
        f"{timeframe} -> "
        f"{confluence['signal']} "
        f"score={confluence['score']} "
        f"confidence={confluence['confidence']}"
    )

final = result["confluence"]

print()
print("FINAL SIGNAL:", final["signal"])
print("FINAL SCORE:", final["score"])
print("FINAL CONFIDENCE:", final["confidence"])
print("FINAL REASONS:", final["reasons"])

assert final["signal"] == "LONG"
assert final["score"] == 36
assert final["confidence"] == 60

print()
print("REAL MTF BULLISH TEST: SUCCESS")
