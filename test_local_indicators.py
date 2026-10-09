from analysis.indicators.local_indicators import (
    analyze_local,
    atr,
    ema,
    macd,
    rsi,
    sma,
    support_resistance,
    trend,
    volatility,
)


def candles(count=100):
    result = []

    for i in range(count):
        base = 100 + i
        result.append(
            {
                "datetime": f"2026-10-08 06:{i:02d}:00",
                "open": base,
                "high": base + 2,
                "low": base - 1,
                "close": base + 1,
                "volume": 1000,
            }
        )

    return result


DATA = candles()


def test_sma():
    assert sma(DATA, 20) is not None
    print("test_sma: PASS")


def test_ema():
    assert ema(DATA, 20) is not None
    print("test_ema: PASS")


def test_rsi():
    value = rsi(DATA, 14)
    assert value == 100.0
    print("test_rsi: PASS")


def test_atr():
    value = atr(DATA, 14)
    assert value is not None
    assert value > 0
    print("test_atr: PASS")


def test_volatility():
    value = volatility(DATA, 20)
    assert value is not None
    assert value > 0
    print("test_volatility: PASS")


def test_macd():
    value = macd(DATA)
    assert value is not None
    assert "macd" in value
    assert "signal" in value
    assert "histogram" in value
    print("test_macd: PASS")


def test_trend():
    assert trend(DATA) == "BULLISH"
    print("test_trend: PASS")


def test_support_resistance():
    value = support_resistance(DATA, 20)

    assert value is not None
    assert value["support"] < value["resistance"]

    print("test_support_resistance: PASS")


def test_analyze_local():
    value = analyze_local(DATA)

    assert "ema_20" in value
    assert "rsi_14" in value
    assert "macd" in value
    assert "atr_14" in value
    assert "trend" in value

    print("test_analyze_local: PASS")


if __name__ == "__main__":
    test_sma()
    test_ema()
    test_rsi()
    test_atr()
    test_volatility()
    test_macd()
    test_trend()
    test_support_resistance()
    test_analyze_local()
    print("STEP 9A LOCAL INDICATOR TESTS: PASS")
