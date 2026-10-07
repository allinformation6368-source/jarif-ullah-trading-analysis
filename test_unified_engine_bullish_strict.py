from analysis.unified_engine import analyze_timeframe

candles = [
    # Initial structure
    {"datetime": "2026-10-07T09:15:00", "open": 100, "high": 103, "low": 99, "close": 101},
    {"datetime": "2026-10-07T09:20:00", "open": 101, "high": 105, "low": 99, "close": 103},

    # Swing LOW #1 = 97
    {"datetime": "2026-10-07T09:25:00", "open": 103, "high": 106, "low": 97, "close": 100},

    # Higher than 97
    {"datetime": "2026-10-07T09:30:00", "open": 100, "high": 104, "low": 100, "close": 102},

    # Higher than 97
    {"datetime": "2026-10-07T09:35:00", "open": 102, "high": 107, "low": 101, "close": 105},

    # Swing LOW #2 = 97
    {"datetime": "2026-10-07T09:40:00", "open": 105, "high": 106, "low": 97, "close": 103},

    # Higher than 97 + swing HIGH candidate
    {"datetime": "2026-10-07T09:45:00", "open": 103, "high": 109, "low": 102, "close": 108},

    # Higher than 97
    {"datetime": "2026-10-07T09:50:00", "open": 108, "high": 108, "low": 103, "close": 104},

    # SSL SWEEP: breaks 97
    {"datetime": "2026-10-07T09:55:00", "open": 104, "high": 106, "low": 95, "close": 103},

    # Strong bullish displacement
    {"datetime": "2026-10-07T10:00:00", "open": 103, "high": 112, "low": 102, "close": 111},

    # Bullish MSS: close above previous swing high 109
    {"datetime": "2026-10-07T10:05:00", "open": 111, "high": 115, "low": 110, "close": 114},

    # Bullish continuation / FVG
    {"datetime": "2026-10-07T10:10:00", "open": 114, "high": 117, "low": 112, "close": 116},

    # Pullback
    {"datetime": "2026-10-07T10:15:00", "open": 116, "high": 117, "low": 108, "close": 110},

    # Final price in DISCOUNT
    {"datetime": "2026-10-07T10:20:00", "open": 110, "high": 112, "low": 96, "close": 100},
]

try:
    result = analyze_timeframe(candles)

    print("STRICT BULLISH END-TO-END TEST: SUCCESS")
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
    print("STRICT BULLISH END-TO-END TEST: FAILED")
    traceback.print_exc()
