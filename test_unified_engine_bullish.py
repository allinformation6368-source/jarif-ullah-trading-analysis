from analysis.unified_engine import analyze_timeframe

candles = [
    {"datetime": "2026-10-07T09:15:00", "open": 100, "high": 103, "low": 99, "close": 101},
    {"datetime": "2026-10-07T09:20:00", "open": 101, "high": 105, "low": 99, "close": 103},
    {"datetime": "2026-10-07T09:25:00", "open": 103, "high": 106, "low": 97, "close": 102},
    {"datetime": "2026-10-07T09:30:00", "open": 102, "high": 104, "low": 99, "close": 100},
    {"datetime": "2026-10-07T09:35:00", "open": 100, "high": 105, "low": 97, "close": 103},

    # Previous high / structure area
    {"datetime": "2026-10-07T09:40:00", "open": 103, "high": 108, "low": 101, "close": 106},
    {"datetime": "2026-10-07T09:45:00", "open": 106, "high": 107, "low": 99, "close": 102},

    # SSL sweep + bullish displacement
    {"datetime": "2026-10-07T09:50:00", "open": 102, "high": 110, "low": 95, "close": 109},

    # Pullback
    {"datetime": "2026-10-07T09:55:00", "open": 109, "high": 110, "low": 103, "close": 105},

    # Bullish FVG setup
    {"datetime": "2026-10-07T10:00:00", "open": 105, "high": 107, "low": 104, "close": 106},
    {"datetime": "2026-10-07T10:05:00", "open": 106, "high": 114, "low": 108, "close": 113},

    # Strong bullish continuation / MSS
    {"datetime": "2026-10-07T10:10:00", "open": 113, "high": 116, "low": 110, "close": 115},

    # Pullback
    {"datetime": "2026-10-07T10:15:00", "open": 115, "high": 116, "low": 106, "close": 109},

    # Final price in discount
    {"datetime": "2026-10-07T10:20:00", "open": 109, "high": 112, "low": 98, "close": 100},
]

try:
    result = analyze_timeframe(candles)

    print("BULLISH END-TO-END TEST: SUCCESS")
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
    print("BULLISH END-TO-END TEST: FAILED")
    traceback.print_exc()
