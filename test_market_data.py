from data.market_data import (
    fetch_market_data,
    fetch_multi_timeframe_data,
)


def test_fetch_market_data_uses_provider(monkeypatch):
    def fake_fetch(
        symbol,
        interval,
        outputsize,
    ):
        assert symbol == "BTC/USD"
        assert interval == "1min"
        assert outputsize == 10

        return {
            "status": "VALID",
            "candles": [
                {
                    "datetime": "2026-01-01 00:00:00",
                    "open": 100.0,
                    "high": 110.0,
                    "low": 95.0,
                    "close": 105.0,
                    "volume": None,
                }
            ],
            "meta": {},
        }

    monkeypatch.setattr(
        "data.market_data.fetch_twelve_data_candles",
        fake_fetch,
    )

    result = fetch_market_data(
        "BTC/USD",
        "1min",
        outputsize=10,
    )

    assert result["status"] == "VALID"
    assert result["provider"] == "twelvedata"
    assert result["symbol"] == "BTC/USD"
    assert len(result["candles"]) == 1


def test_fetch_market_data_rejects_unknown_provider():
    result = fetch_market_data(
        "BTC/USD",
        "1min",
        provider="unknown",
    )

    assert result["status"] == "REJECTED"
    assert "Unsupported data provider" in result["reason"]


def test_fetch_market_data_propagates_provider_error(monkeypatch):
    def fake_fetch(
        symbol,
        interval,
        outputsize,
    ):
        return {
            "status": "REJECTED",
            "reason": "API unavailable",
        }

    monkeypatch.setattr(
        "data.market_data.fetch_twelve_data_candles",
        fake_fetch,
    )

    result = fetch_market_data(
        "BTC/USD",
        "1min",
    )

    assert result["status"] == "REJECTED"
    assert result["reason"] == "API unavailable"


def test_fetch_multi_timeframe_data(monkeypatch):
    def fake_fetch(
        symbol,
        interval,
        outputsize,
    ):
        return {
            "status": "VALID",
            "candles": [
                {
                    "datetime": "2026-01-01 00:00:00",
                    "open": 100.0,
                    "high": 110.0,
                    "low": 95.0,
                    "close": 105.0,
                    "volume": None,
                }
            ],
        }

    monkeypatch.setattr(
        "data.market_data.fetch_twelve_data_candles",
        fake_fetch,
    )

    result = fetch_multi_timeframe_data(
        "BTC/USD",
        ["1min", "5min", "15min"],
    )

    assert result["status"] == "VALID"
    assert set(result["timeframes"]) == {
        "1min",
        "5min",
        "15min",
    }


def test_fetch_multi_timeframe_requires_list():
    result = fetch_multi_timeframe_data(
        "BTC/USD",
        "1min",
    )

    assert result["status"] == "REJECTED"
    assert result["reason"] == (
        "Timeframes must be a list or tuple"
    )


def test_fetch_multi_timeframe_stops_on_failure(monkeypatch):
    def fake_fetch(
        symbol,
        interval,
        outputsize,
    ):
        if interval == "5min":
            return {
                "status": "REJECTED",
                "reason": "Rate limit",
            }

        return {
            "status": "VALID",
            "candles": [],
        }

    monkeypatch.setattr(
        "data.market_data.fetch_twelve_data_candles",
        fake_fetch,
    )

    result = fetch_multi_timeframe_data(
        "BTC/USD",
        ["1min", "5min", "15min"],
    )

    assert result["status"] == "REJECTED"
    assert "5min" in result["reason"]
