from analysis.unified_engine import analyze_timeframe

candles = [
    {"datetime": "2026-10-07T09:15:00", "open": 100, "high": 103, "low": 99, "close": 102},
    {"datetime": "2026-10-07T09:20:00", "open": 102, "high": 106, "low": 101, "close": 105},
    {"datetime": "2026-10-07T09:25:00", "open": 105, "high": 108, "low": 103, "close": 104},
    {"datetime": "2026-10-07T09:30:00", "open": 104, "high": 106, "low": 100, "close": 101},
    {"datetime": "2026-10-07T09:35:00", "open": 101, "high": 103, "low": 98, "close": 100},
    {"datetime": "2026-10-07T09:40:00", "open": 100, "high": 108, "low": 99, "close": 106},
    {"datetime": "2026-10-07T09:45:00", "open": 106, "high": 108, "low": 102, "close": 104},
    {"datetime": "2026-10-07T09:50:00", "open": 104, "high": 107, "low": 101, "close": 103},
    {"datetime": "2026-10-07T09:55:00", "open": 103, "high": 109, "low": 102, "close": 108},
    {"datetime": "2026-10-07T10:00:00", "open": 108, "high": 111, "low": 106, "close": 110},
    {"datetime": "2026-10-07T10:05:00", "open": 110, "high": 113, "low": 107, "close": 112},
    {"datetime": "2026-10-07T10:10:00", "open": 112, "high": 114, "low": 109, "close": 110},
    {"datetime": "2026-10-07T10:15:00", "open": 110, "high": 115, "low": 108, "close": 109},
    {"datetime": "2026-10-07T10:20:00", "open": 109, "high": 116, "low": 107, "close": 108},

    # BSL sweep
    {"datetime": "2026-10-07T10:25:00", "open": 108, "high": 117, "low": 107, "close": 110},

    # Strong bearish displacement
    {"datetime": "2026-10-07T10:30:00", "open": 110, "high": 111, "low": 100, "close": 101},

    # Break previous swing low (MSS)
    {"datetime": "2026-10-07T10:35:00", "open": 101, "high": 102, "low": 94, "close": 95},

    # Final price in premium
    {"datetime": "2026-10-07T10:40:00", "open": 95, "high": 110, "low": 94, "close": 108},
]

try:
    result = analyze_timeframe(candles)

    print("BEARISH END-TO-END TEST: SUCCESS")
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

except Exception:
    import traceback
    print("BEARISH END-TO-END TEST: FAILED")
    traceback.print_exc()
