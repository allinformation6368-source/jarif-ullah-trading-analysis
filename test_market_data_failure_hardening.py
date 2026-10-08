import json
from io import BytesIO
from urllib.error import HTTPError, URLError

import data.twelve_data as twelve_data
from data.market_data import (
    fetch_market_data,
    fetch_multi_timeframe_data,
)
from data.twelve_data import (
    fetch_twelve_data_candles,
    parse_twelve_data_response,
)


def test_parse_rejects_non_dict_response():
    result = parse_twelve_data_response(None)

    assert result["status"] == "REJECTED"
    assert result["reason"] == "Invalid TwelveData response"


def test_parse_rejects_failed_api_status():
    result = parse_twelve_data_response(
        {
            "status": "error",
            "message": "Invalid symbol",
        }
    )

    assert result["status"] == "REJECTED"
    assert result["reason"] == "Invalid symbol"


def test_parse_rejects_missing_values():
    result = parse_twelve_data_response(
        {
            "status": "ok",
        }
    )

    assert result["status"] == "REJECTED"
    assert result["reason"] == "Missing TwelveData values"


def test_parse_rejects_malformed_candles():
    result = parse_twelve_data_response(
        {
            "status": "ok",
            "values": [
                {
                    "datetime": "2026-01-01",
                    "open": "100",
                }
            ],
        }
    )

    assert result["status"] == "REJECTED"


def test_fetch_rejects_missing_api_key(monkeypatch):
    monkeypatch.setattr(
        twelve_data,
        "TWELVE_DATA_API_KEY",
        None,
    )

    result = fetch_twelve_data_candles(
        symbol="BTC/USD",
        interval="1min",
    )

    assert result["status"] == "REJECTED"
    assert result["reason"] == "TwelveData API key is not configured"


def test_fetch_rejects_invalid_symbol():
    result = fetch_twelve_data_candles(
        symbol="",
        interval="1min",
        api_key="test-key",
    )

    assert result["status"] == "REJECTED"
    assert result["reason"] == "Invalid symbol"


def test_fetch_rejects_invalid_interval():
    result = fetch_twelve_data_candles(
        symbol="BTC/USD",
        interval="",
        api_key="test-key",
    )

    assert result["status"] == "REJECTED"
    assert result["reason"] == "Invalid interval"


def test_fetch_rejects_invalid_outputsize():
    result = fetch_twelve_data_candles(
        symbol="BTC/USD",
        interval="1min",
        outputsize=0,
        api_key="test-key",
    )

    assert result["status"] == "REJECTED"
    assert result["reason"] == "Invalid outputsize"


def test_fetch_handles_http_error(monkeypatch):
    def fake_urlopen(*args, **kwargs):
        raise HTTPError(
            url="https://example.com",
            code=401,
            msg="Unauthorized",
            hdrs=None,
            fp=None,
        )

    monkeypatch.setattr(twelve_data, "urlopen", fake_urlopen)

    result = fetch_twelve_data_candles(
        symbol="BTC/USD",
        interval="1min",
        api_key="test-key",
    )

    assert result["status"] == "REJECTED"
    assert result["reason"] == "HTTP error: 401"


def test_fetch_handles_network_error(monkeypatch):
    def fake_urlopen(*args, **kwargs):
        raise URLError("Connection failed")

    monkeypatch.setattr(twelve_data, "urlopen", fake_urlopen)

    result = fetch_twelve_data_candles(
        symbol="BTC/USD",
        interval="1min",
        api_key="test-key",
    )

    assert result["status"] == "REJECTED"
    assert result["reason"] == "Network error: Connection failed"


def test_fetch_handles_timeout(monkeypatch):
    def fake_urlopen(*args, **kwargs):
        raise TimeoutError()

    monkeypatch.setattr(twelve_data, "urlopen", fake_urlopen)

    result = fetch_twelve_data_candles(
        symbol="BTC/USD",
        interval="1min",
        api_key="test-key",
    )

    assert result["status"] == "REJECTED"
    assert result["reason"] == "Request timeout"


def test_fetch_handles_invalid_json(monkeypatch):
    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return b"not-json"

    monkeypatch.setattr(
        twelve_data,
        "urlopen",
        lambda *args, **kwargs: FakeResponse(),
    )

    result = fetch_twelve_data_candles(
        symbol="BTC/USD",
        interval="1min",
        api_key="test-key",
    )

    assert result["status"] == "REJECTED"
    assert result["reason"] == "Invalid JSON response"


def test_fetch_accepts_valid_response(monkeypatch):
    payload = {
        "status": "ok",
        "meta": {
            "symbol": "BTC/USD",
        },
        "values": [
            {
                "datetime": "2026-01-01 00:00:00",
                "open": "100",
                "high": "105",
                "low": "95",
                "close": "102",
                "volume": "10",
            }
        ],
    }

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return json.dumps(payload).encode()

    monkeypatch.setattr(
        twelve_data,
        "urlopen",
        lambda *args, **kwargs: FakeResponse(),
    )

    result = fetch_twelve_data_candles(
        symbol="BTC/USD",
        interval="1min",
        api_key="test-key",
    )

    assert result["status"] == "VALID"
    assert len(result["candles"]) == 1


def test_market_data_rejects_unsupported_provider():
    result = fetch_market_data(
        symbol="BTC/USD",
        timeframe="1min",
        provider="unknown",
    )

    assert result["status"] == "REJECTED"
    assert "Unsupported data provider" in result["reason"]


def test_multi_timeframe_rejects_invalid_timeframes():
    result = fetch_multi_timeframe_data(
        symbol="BTC/USD",
        timeframes="1min",
    )

    assert result["status"] == "REJECTED"
    assert result["reason"] == "Timeframes must be a list or tuple"


def test_multi_timeframe_stops_on_provider_failure(monkeypatch):
    monkeypatch.setattr(
        "data.market_data.fetch_market_data",
        lambda **kwargs: {
            "status": "REJECTED",
            "reason": "Synthetic provider failure",
        },
    )

    result = fetch_multi_timeframe_data(
        symbol="BTC/USD",
        timeframes=["1min", "5min"],
    )

    assert result["status"] == "REJECTED"
    assert "Failed timeframe 1min" in result["reason"]
    assert "Synthetic provider failure" in result["reason"]
