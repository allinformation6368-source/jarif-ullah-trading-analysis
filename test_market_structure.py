from analysis.market_structure import (
    analyze_market_structure,
    liquidity_levels,
    liquidity_sweep,
    market_structure_shift,
    structure_bias,
    swing_points,
)


def candle(i, high, low, close):
    return {
        "datetime": f"2026-10-08 06:{i:02d}:00",
        "open": close,
        "high": high,
        "low": low,
        "close": close,
    }


def base_data():
    return [
        candle(0, 100, 95, 98),
        candle(1, 102, 96, 100),
        candle(2, 105, 98, 103),
        candle(3, 101, 97, 99),
        candle(4, 108, 100, 106),
        candle(5, 103, 99, 101),
        candle(6, 111, 102, 109),
        candle(7, 106, 101, 104),
        candle(8, 114, 105, 112),
    ]


def test_swing_points():
    result = swing_points(base_data(), left=1, right=1)

    assert result["swing_highs"]
    assert result["swing_lows"]

    print("test_swing_points: PASS")


def test_structure_bias():
    result = structure_bias(base_data(), left=1, right=1)

    assert result == "BULLISH"

    print("test_structure_bias: PASS")


def test_liquidity_levels():
    result = liquidity_levels(base_data(), left=1, right=1)

    assert result["buy_side_liquidity"] is not None
    assert result["sell_side_liquidity"] is not None

    print("test_liquidity_levels: PASS")


def test_bearish_sweep():
    data = base_data()

    data.append(candle(9, 116, 108, 109))

    result = liquidity_sweep(data, left=1, right=1)

    assert result["sweep"] is True
    assert result["direction"] == "BEARISH"

    print("test_bearish_sweep: PASS")


def test_bullish_sweep():
    data = [
        candle(0, 105, 100, 103),
        candle(1, 106, 99, 102),
        candle(2, 108, 101, 106),
        candle(3, 107, 98, 104),
        candle(4, 110, 100, 108),
        candle(5, 106, 97, 99),
        candle(6, 109, 95, 99),
    ]

    result = liquidity_sweep(data, left=1, right=1)

    assert result["sweep"] is True
    assert result["direction"] == "BULLISH"

    print("test_bullish_sweep: PASS")


def test_mss():
    data = base_data()

    data.append(candle(9, 118, 110, 117))

    result = market_structure_shift(data, left=1, right=1)

    assert result["mss"] is True
    assert result["direction"] == "BULLISH"

    print("test_mss: PASS")


def test_combined_analysis():
    result = analyze_market_structure(base_data())

    assert "structure" in result
    assert "swing_points" in result
    assert "liquidity" in result
    assert "sweep" in result
    assert "mss" in result

    print("test_combined_analysis: PASS")


if __name__ == "__main__":
    test_swing_points()
    test_structure_bias()
    test_liquidity_levels()
    test_bearish_sweep()
    test_bullish_sweep()
    test_mss()
    test_combined_analysis()

    print("STEP 9B MARKET STRUCTURE TESTS: PASS")
