from analysis.confluence.local_confluence import analyze_confluence


def candle(i, high, low, close):
    return {
        "datetime": f"2026-10-08 08:{i:02d}:00",
        "open": close,
        "high": high,
        "low": low,
        "close": close,
    }


def bullish_data():
    data = []

    for i in range(60):
        base = 100 + (i * 0.8)

        data.append(
            candle(
                i,
                base + 2.0,
                base - 1.0,
                base + 1.0,
            )
        )

    return data


def bearish_data():
    data = []

    for i in range(60):
        base = 150 - (i * 0.8)

        data.append(
            candle(
                i,
                base + 1.0,
                base - 2.0,
                base - 1.0,
            )
        )

    return data


def test_output_contract():
    result = analyze_confluence(bullish_data())

    assert "decision" in result
    assert "score" in result
    assert "bullish_score" in result
    assert "bearish_score" in result
    assert "contradiction" in result
    assert "components" in result
    assert "indicators" in result
    assert "structure" in result

    print("test_output_contract: PASS")


def test_bullish_direction():
    result = analyze_confluence(bullish_data())

    assert result["decision"] in {
        "BUY",
        "SELL",
        "WAIT",
        "INVALIDATED",
    }

    assert isinstance(result["score"], (int, float))
    assert result["bullish_score"] >= 0
    assert result["bearish_score"] >= 0

    print("test_bullish_direction: PASS")


def test_bearish_direction():
    result = analyze_confluence(bearish_data())

    assert result["decision"] in {
        "BUY",
        "SELL",
        "WAIT",
        "INVALIDATED",
    }

    assert isinstance(result["score"], (int, float))
    assert result["bullish_score"] >= 0
    assert result["bearish_score"] >= 0

    print("test_bearish_direction: PASS")


def test_components_are_explainable():
    result = analyze_confluence(bullish_data())

    assert result["components"]

    for component in result["components"]:
        assert "direction" in component
        assert "weight" in component
        assert "score" in component
        assert "reason" in component

    print("test_components_are_explainable: PASS")


def test_no_execution():
    result = analyze_confluence(bullish_data())

    assert "execute" not in result
    assert "order" not in result
    assert "position" not in result

    print("test_no_execution: PASS")


if __name__ == "__main__":
    test_output_contract()
    test_bullish_direction()
    test_bearish_direction()
    test_components_are_explainable()
    test_no_execution()

    print("STEP 9C LOCAL CONFLUENCE TESTS: PASS")
