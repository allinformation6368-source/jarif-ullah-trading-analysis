from analysis.market_regime import detect_market_regime


def make_bullish():
    return [
        {"open": 100, "high": 102, "low": 99, "close": 101},
        {"open": 101, "high": 104, "low": 100, "close": 103},
        {"open": 103, "high": 107, "low": 102, "close": 106},
        {"open": 106, "high": 110, "low": 105, "close": 109},
    ]


def make_bearish():
    return [
        {"open": 109, "high": 110, "low": 106, "close": 108},
        {"open": 108, "high": 109, "low": 103, "close": 104},
        {"open": 104, "high": 105, "low": 100, "close": 101},
        {"open": 101, "high": 102, "low": 96, "close": 97},
    ]


def make_ranging():
    return [
        {"open": 100, "high": 105, "low": 95, "close": 100},
        {"open": 100, "high": 104, "low": 96, "close": 101},
        {"open": 101, "high": 105, "low": 95, "close": 99},
        {"open": 99, "high": 104, "low": 96, "close": 100},
    ]


def test_bullish_regime():
    result = detect_market_regime(make_bullish())

    assert result["status"] == "VALID"
    assert result["regime"] == "TRENDING_BULLISH"


def test_bearish_regime():
    result = detect_market_regime(make_bearish())

    assert result["status"] == "VALID"
    assert result["regime"] == "TRENDING_BEARISH"


def test_ranging_regime():
    result = detect_market_regime(make_ranging())

    assert result["status"] == "VALID"
    assert result["regime"] == "RANGING"


def test_insufficient_candles():
    result = detect_market_regime([])

    assert result["status"] == "WAIT"
    assert result["regime"] == "NEUTRAL"


def test_flat_market_is_neutral():
    candles = [
        {"open": 100, "high": 100, "low": 100, "close": 100},
        {"open": 100, "high": 100, "low": 100, "close": 100},
        {"open": 100, "high": 100, "low": 100, "close": 100},
        {"open": 100, "high": 100, "low": 100, "close": 100},
    ]

    result = detect_market_regime(candles)

    assert result["status"] == "VALID"
    assert result["regime"] == "NEUTRAL"


if __name__ == "__main__":
    test_bullish_regime()
    test_bearish_regime()
    test_ranging_regime()
    test_insufficient_candles()
    test_flat_market_is_neutral()
    print("MARKET REGIME CONTRACT TEST: SUCCESS")
