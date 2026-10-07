from analysis.unified_engine import analyze_timeframe

candles = [
    {"datetime": "2026-10-07T09:15:00", "open": 100, "high": 103, "low": 99, "close": 102},
    {"datetime": "2026-10-07T09:20:00", "open": 102, "high": 105, "low": 101, "close": 104},
    {"datetime": "2026-10-07T09:25:00", "open": 104, "high": 106, "low": 102, "close": 103},
    {"datetime": "2026-10-07T09:30:00", "open": 103, "high": 107, "low": 102, "close": 106},
    {"datetime": "2026-10-07T09:35:00", "open": 106, "high": 109, "low": 105, "close": 108},
    {"datetime": "2026-10-07T09:40:00", "open": 108, "high": 110, "low": 106, "close": 107},
    {"datetime": "2026-10-07T09:45:00", "open": 107, "high": 112, "low": 106, "close": 111},
    {"datetime": "2026-10-07T09:50:00", "open": 111, "high": 114, "low": 109, "close": 113},
    {"datetime": "2026-10-07T09:55:00", "open": 113, "high": 115, "low": 110, "close": 111},
    {"datetime": "2026-10-07T10:00:00", "open": 111, "high": 116, "low": 109, "close": 115},
]

try:
    result = analyze_timeframe(candles)

    print("REAL DATA TEST: SUCCESS")
    print()
    print("Structure:", result["structure"])
    print("Liquidity:", result["liquidity"])
    print("Sweeps:", result["sweeps"])
    print("MSS:", result["mss"])
    print("FVGs:", result["fvgs"])
    print("Order Blocks:", result["order_blocks"])
    print("Premium/Discount:", result["premium_discount"])
    print("Displacement:", result["displacement"])
    print("Confluence:", result["confluence"])

except Exception as e:
    import traceback
    print("REAL DATA TEST: FAILED")
    traceback.print_exc()
