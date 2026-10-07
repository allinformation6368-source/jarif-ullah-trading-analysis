from strategies.confluence import calculate_confluence


def run_test(name, structure, sweeps, mss, fvgs, order_blocks, pd, displacement):
    result = calculate_confluence(
        structure,
        sweeps,
        mss,
        fvgs,
        order_blocks,
        pd,
        displacement
    )

    print(name)
    print("Signal:", result["signal"])
    print("Score:", result["score"])
    print("Confidence:", result["confidence"])
    print("Reasons:", result["reasons"])
    print()


# PURE BULLISH SETUP
run_test(
    "PURE BULLISH TEST",
    {"bias": "BULLISH"},
    [{"type": "SSL_SWEEP"}],
    [{"type": "BULLISH_MSS"}],
    [{"type": "BULLISH_FVG"}],
    [{"type": "BULLISH_OB"}],
    {"zone": "DISCOUNT"},
    [{"type": "BULLISH"}],
)


# PURE BEARISH SETUP
run_test(
    "PURE BEARISH TEST",
    {"bias": "BEARISH"},
    [{"type": "BSL_SWEEP"}],
    [{"type": "BEARISH_MSS"}],
    [{"type": "BEARISH_FVG"}],
    [{"type": "BEARISH_OB"}],
    {"zone": "PREMIUM"},
    [{"type": "BEARISH"}],
)


# CONFLICTING SETUP
run_test(
    "CONFLICTING TEST",
    {"bias": "BULLISH"},
    [{"type": "SSL_SWEEP"}],
    [{"type": "BULLISH_MSS"}],
    [
        {"type": "BULLISH_FVG"},
        {"type": "BEARISH_FVG"},
    ],
    [
        {"type": "BULLISH_OB"},
        {"type": "BEARISH_OB"},
    ],
    {"zone": "DISCOUNT"},
    [
        {"type": "BULLISH"},
        {"type": "BEARISH"},
    ],
)


# BULLISH MSS WITH LATER OPPOSITE ARTIFACTS
# Expected: bullish directional evidence remains relevant.
run_test(
    "BULLISH MSS WITH LATER OPPOSITE ARTIFACTS",
    {"bias": "BEARISH"},
    [{"type": "SSL_SWEEP"}],
    [{"type": "BULLISH_MSS"}],
    [
        {"type": "BULLISH_FVG", "index": 10},
    ],
    [
        {"type": "BULLISH_OB", "index": 8},
        {"type": "BEARISH_OB", "index": 11},
    ],
    {"zone": "DISCOUNT"},
    [
        {"type": "BULLISH", "index": 9},
        {"type": "BEARISH", "index": 13},
    ],
)
