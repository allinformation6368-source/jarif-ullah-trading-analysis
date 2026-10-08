from data.mtf_market_data import (
    get_mode_timeframes,
    fetch_mode_market_data,
)


def test_get_mode_timeframes_scalping():
    result = get_mode_timeframes("scalping")

    assert result["status"] == "VALID"
    assert result["timeframes"] == [
        "1min",
        "5min",
        "15min",
        "1h",
    ]


def test_get_mode_timeframes_intraday():
    result = get_mode_timeframes("intraday")

    assert result["status"] == "VALID"
    assert result["timeframes"] == [
        "5min",
        "15min",
        "1h",
        "4h",
    ]


def test_get_mode_timeframes_swing():
    result = get_mode_timeframes("swing")

    assert result["status"] == "VALID"
    assert result["timeframes"] == [
        "4h",
        "1day",
        "1week",
    ]


def test_get_mode_timeframes_rejects_unknown_mode():
    result = get_mode_timeframes("invalid")

    assert result["status"] == "REJECTED"
    assert "Unsupported trading mode" in result["reason"]


def test_fetch_mode_market_data(monkeypatch):
    captured = {}

    def fake_fetch(
        symbol,
        timeframes,
        outputsize,
        provider,
    ):
        captured["symbol"] = symbol
        captured["timeframes"] = timeframes
        captured["outputsize"] = outputsize
        captured["provider"] = provider

        return {
            "status": "VALID",
            "timeframes": {
                timeframe: [
                    {
                        "datetime": "2026-01-01 00:00:00",
                        "open": 100.0,
                        "high": 110.0,
                        "low": 95.0,
                        "close": 105.0,
                        "volume": None,
                    }
                ]
                for timeframe in timeframes
            },
        }

    monkeypatch.setattr(
        "data.mtf_market_data.fetch_multi_timeframe_data",
        fake_fetch,
    )
    monkeypatch.setattr(
        "data.mtf_market_data.validate_latest_candle_freshness",
        lambda candles, timeframe: {
            "status": "VALID",
            "age_seconds": 0,
        },
    )

    result = fetch_mode_market_data(
        symbol="BTC/USD",
        mode="intraday",
        outputsize=100,
    )

    assert result["status"] == "VALID"
    assert result["symbol"] == "BTC/USD"
    assert result["mode"] == "intraday"

    assert captured["symbol"] == "BTC/USD"
    assert captured["timeframes"] == [
        "5min",
        "15min",
        "1h",
        "4h",
    ]
    assert captured["outputsize"] == 100
    assert captured["provider"] == "twelvedata"


def test_fetch_mode_market_data_rejects_invalid_mode(monkeypatch):
    called = False

    def fake_fetch(*args, **kwargs):
        nonlocal called
        called = True
        return {"status": "VALID", "timeframes": {}}

    monkeypatch.setattr(
        "data.mtf_market_data.fetch_multi_timeframe_data",
        fake_fetch,
    )

    result = fetch_mode_market_data(
        symbol="BTC/USD",
        mode="invalid",
    )

    assert result["status"] == "REJECTED"
    assert called is False


def test_fetch_mode_market_data_propagates_provider_failure(monkeypatch):
    def fake_fetch(*args, **kwargs):
        return {
            "status": "REJECTED",
            "reason": "Rate limit",
        }

    monkeypatch.setattr(
        "data.mtf_market_data.fetch_multi_timeframe_data",
        fake_fetch,
    )

    result = fetch_mode_market_data(
        symbol="BTC/USD",
        mode="scalping",
    )

    assert result["status"] == "REJECTED"
    assert result["reason"] == "Rate limit"
