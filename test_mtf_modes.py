from analysis.mtf_confluence import calculate_mtf_confluence


def make_results(timeframes):
    return {
        timeframe: {
            "confluence": {
                "signal": "LONG",
                "score": 10,
            }
        }
        for timeframe in timeframes
    }


# Scalping: 1min=1, 5min=2, 15min=3, 1h=4
scalping = calculate_mtf_confluence(
    make_results(["1min", "5min", "15min", "1h"]),
    mode="scalping",
)

assert scalping["score"] == 100
assert scalping["confidence"] == 100
assert scalping["signal"] == "LONG"

# Intraday: 5min=1, 15min=2, 1h=3, 4h=4
intraday = calculate_mtf_confluence(
    make_results(["5min", "15min", "1h", "4h"]),
    mode="intraday",
)

assert intraday["score"] == 100
assert intraday["confidence"] == 100
assert intraday["signal"] == "LONG"

# Swing: 4h=1, 1day=2, 1week=3
swing = calculate_mtf_confluence(
    make_results(["4h", "1day", "1week"]),
    mode="swing",
)

assert swing["score"] == 60
assert swing["confidence"] == 100
assert swing["signal"] == "LONG"


# Legacy behavior must remain unchanged when mode is omitted.
legacy = calculate_mtf_confluence(
    make_results(["5m", "15m", "1h"]),
)

assert legacy["score"] == 60
assert legacy["confidence"] == 100
assert legacy["signal"] == "LONG"

print("MTF MODE WEIGHT TEST: SUCCESS")
print("Scalping:", scalping)
print("Intraday:", intraday)
print("Swing:", swing)
print("Legacy:", legacy)
