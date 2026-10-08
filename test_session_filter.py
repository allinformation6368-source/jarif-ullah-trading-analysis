from analysis.session_filter import detect_session, validate_session


def make_candle(hour):
    return [
        {
            "datetime": f"2026-10-07T{hour:02d}:30:00+00:00",
            "open": 100,
            "high": 105,
            "low": 95,
            "close": 102,
        }
    ]


def test_asia_session():
    result = detect_session(make_candle(3))

    assert result["status"] == "VALID"
    assert result["session"] == "ASIA"


def test_london_session():
    result = detect_session(make_candle(10))

    assert result["status"] == "VALID"
    assert result["session"] == "LONDON"


def test_new_york_session():
    result = detect_session(make_candle(16))

    assert result["status"] == "VALID"
    assert result["session"] == "NEW_YORK"


def test_off_session():
    result = detect_session(make_candle(22))

    assert result["status"] == "VALID"
    assert result["session"] == "OFF_SESSION"


def test_empty_candles():
    result = detect_session([])

    assert result["status"] == "WAIT"
    assert result["session"] == "UNKNOWN"


def test_invalid_datetime():
    result = detect_session(
        [{"datetime": "invalid"}]
    )

    assert result["status"] == "WAIT"
    assert result["session"] == "UNKNOWN"


def test_allowed_session():
    session = detect_session(make_candle(10))
    result = validate_session(session)

    assert result["status"] == "APPROVED"
    assert result["session"] == "LONDON"


def test_blocked_session():
    session = detect_session(make_candle(22))
    result = validate_session(session)

    assert result["status"] == "BLOCKED"
    assert result["session"] == "OFF_SESSION"
