from data.scanner.timeframe_policy import (
    required_timeframes,
    screening_timeframes,
    deeper_timeframes,
)


def test_scalping():
    assert required_timeframes("scalping") == (
        "1min",
        "5min",
        "15min",
        "1h",
    )
    assert screening_timeframes("scalping") == ("1min", "5min")
    assert deeper_timeframes("scalping") == ("15min", "1h")
    print("test_scalping: PASS")


def test_intraday():
    assert required_timeframes("intraday") == (
        "5min",
        "15min",
        "1h",
        "4h",
    )
    assert screening_timeframes("intraday") == ("5min", "15min")
    assert deeper_timeframes("intraday") == ("1h", "4h")
    print("test_intraday: PASS")


def test_swing():
    assert required_timeframes("swing") == (
        "4h",
        "1day",
        "1week",
    )
    assert screening_timeframes("swing") == ("4h", "1day")
    assert deeper_timeframes("swing") == ("1week",)
    print("test_swing: PASS")


def test_invalid_mode():
    try:
        required_timeframes("invalid")
        raise AssertionError("invalid mode accepted")
    except ValueError:
        pass

    print("test_invalid_mode: PASS")


if __name__ == "__main__":
    test_scalping()
    test_intraday()
    test_swing()
    test_invalid_mode()
    print("TIMEFRAME POLICY TESTS: PASS")
