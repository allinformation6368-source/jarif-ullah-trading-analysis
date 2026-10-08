from data.twelve_data import (
    _build_time_series_url,
    fetch_twelve_data_candles,
    parse_twelve_data_response,
)


def valid_response():
    return {
        "status": "ok",
        "meta": {
            "symbol": "BTC/USD",
            "interval": "1min",
        },
        "values": [
            {
                "datetime": "2026-01-01 00:00:00",
                "open": "100",
                "high": "110",
                "low": "95",
                "close": "105",
                "volume": "1000",
            }
        ],
    }


def test_build_time_series_url():
    url = _build_time_series_url(
        "BTC/USD",
        "1min",
        50,
    )

    assert url.startswith(
        "https://api.twelvedata.com/time_series?"
    )
    assert "symbol=BTC%2FUSD" in url
    assert "interval=1min" in url
    assert "outputsize=50" in url


def test_parse_orders_candles_chronologically():
    response = valid_response()
    response["values"] = [
        {
            "datetime": "2026-01-01 02:00:00",
            "open": "102",
            "high": "110",
            "low": "100",
            "close": "108",
        },
        {
            "datetime": "2026-01-01 01:00:00",
            "open": "101",
            "high": "105",
            "low": "99",
            "close": "102",
        },
    ]

    result = parse_twelve_data_response(response)

    assert result["status"] == "VALID"
    assert [
        candle["datetime"]
        for candle in result["candles"]
    ] == [
        "2026-01-01 01:00:00",
        "2026-01-01 02:00:00",
    ]


def test_parse_valid_response():
    result = parse_twelve_data_response(
        valid_response()
    )

    assert result["status"] == "VALID"
    assert len(result["candles"]) == 1
    assert result["candles"][0]["close"] == 105.0
    assert result["meta"]["symbol"] == "BTC/USD"


def test_parse_error_response():
    result = parse_twelve_data_response(
        {
            "status": "error",
            "message": "Invalid symbol",
        }
    )

    assert result["status"] == "REJECTED"
    assert result["reason"] == "Invalid symbol"


def test_parse_missing_values():
    result = parse_twelve_data_response(
        {
            "status": "ok",
            "meta": {},
        }
    )

    assert result["status"] == "REJECTED"
    assert result["reason"] == "Missing TwelveData values"


def test_parse_invalid_candle():
    response = valid_response()
    response["values"][0]["close"] = "bad"

    result = parse_twelve_data_response(response)

    assert result["status"] == "REJECTED"


def test_invalid_symbol():
    result = fetch_twelve_data_candles(
        "",
        "1min",
        api_key="test",
    )

    assert result["status"] == "REJECTED"
    assert result["reason"] == "Invalid symbol"


def test_invalid_interval():
    result = fetch_twelve_data_candles(
        "BTC/USD",
        "",
        api_key="test",
    )

    assert result["status"] == "REJECTED"
    assert result["reason"] == "Invalid interval"


def test_invalid_outputsize():
    result = fetch_twelve_data_candles(
        "BTC/USD",
        "1min",
        outputsize=0,
        api_key="test",
    )

    assert result["status"] == "REJECTED"
    assert result["reason"] == "Invalid outputsize"


def test_missing_api_key():
    result = fetch_twelve_data_candles(
        "BTC/USD",
        "1min",
        api_key="",
    )

    assert result["status"] == "REJECTED"
    assert result["reason"] == (
        "TwelveData API key is not configured"
    )
