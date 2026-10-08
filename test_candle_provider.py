from data.candle_provider import (
    normalize_candle,
    normalize_candles,
    validate_candle,
)


def valid_candle():
    return {
        "datetime": "2026-01-01T00:00:00+00:00",
        "open": 100,
        "high": 110,
        "low": 95,
        "close": 105,
        "volume": 1000,
    }


def test_validate_valid_candle():
    result = validate_candle(valid_candle())

    assert result["status"] == "VALID"


def test_validate_missing_field():
    candle = valid_candle()
    del candle["close"]

    result = validate_candle(candle)

    assert result["status"] == "REJECTED"
    assert "Missing candle field" in result["reason"]


def test_validate_invalid_price():
    candle = valid_candle()
    candle["close"] = "invalid"

    result = validate_candle(candle)

    assert result["status"] == "REJECTED"
    assert result["reason"] == "Invalid candle price"


def test_validate_negative_price():
    candle = valid_candle()
    candle["low"] = -1

    result = validate_candle(candle)

    assert result["status"] == "REJECTED"
    assert result["reason"] == "Candle prices must be positive"


def test_validate_invalid_high():
    candle = valid_candle()
    candle["high"] = 101

    result = validate_candle(candle)

    assert result["status"] == "REJECTED"
    assert result["reason"] == "Invalid candle high"


def test_validate_invalid_low():
    candle = valid_candle()
    candle["low"] = 106

    result = validate_candle(candle)

    assert result["status"] == "REJECTED"
    assert result["reason"] == "Invalid candle low"


def test_validate_invalid_datetime():
    candle = valid_candle()
    candle["datetime"] = "not-a-date"

    result = validate_candle(candle)

    assert result["status"] == "REJECTED"
    assert result["reason"] == "Invalid candle datetime"


def test_normalize_candle():
    result = normalize_candle(valid_candle())

    assert result["status"] == "VALID"
    assert result["candle"]["open"] == 100.0
    assert result["candle"]["close"] == 105.0
    assert result["candle"]["volume"] == 1000.0


def test_normalize_candle_without_volume():
    candle = valid_candle()
    del candle["volume"]

    result = normalize_candle(candle)

    assert result["status"] == "VALID"
    assert result["candle"]["volume"] is None


def test_normalize_candles():
    result = normalize_candles(
        [
            valid_candle(),
            {
                **valid_candle(),
                "datetime": "2026-01-01T00:01:00+00:00",
            },
        ]
    )

    assert result["status"] == "VALID"
    assert len(result["candles"]) == 2


def test_normalize_candles_invalid_input():
    result = normalize_candles("invalid")

    assert result["status"] == "REJECTED"
    assert result["reason"] == "Candles must be a list"


def test_normalize_candles_rejects_invalid_item():
    result = normalize_candles(
        [
            valid_candle(),
            {
                "datetime": "bad",
            },
        ]
    )

    assert result["status"] == "REJECTED"


def test_validate_non_dict():
    result = validate_candle(None)

    assert result["status"] == "REJECTED"
    assert result["reason"] == "Invalid candle"
