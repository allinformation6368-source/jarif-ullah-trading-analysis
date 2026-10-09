from data.scanner.market_cache import MarketDataCache


def test_cache_miss_then_hit():
    cache = MarketDataCache(
        ttl_seconds={"1min": 60}
    )

    miss = cache.get("BTC/USD", "1min")
    assert miss["status"] == "MISS"

    cache.put(
        "BTC/USD",
        "1min",
        [{"datetime": "2026-10-08T00:00:00+00:00"}],
    )

    hit = cache.get("BTC/USD", "1min")

    assert hit["status"] == "HIT"
    assert len(hit["candles"]) == 1


def test_cache_stats():
    cache = MarketDataCache()

    cache.put(
        "ETH/USD",
        "5min",
        [{"datetime": "2026-10-08T00:00:00+00:00"}],
    )

    stats = cache.stats()

    assert stats["entries"] == 1
    assert stats["keys"][0]["symbol"] == "ETH/USD"
    assert stats["keys"][0]["timeframe"] == "5min"
