import requests

from config.settings import TWELVE_DATA_API_KEY


BASE_URL = "https://api.twelvedata.com"


def get_candles(symbol, interval="15min", outputsize=100):
    response = requests.get(
        f"{BASE_URL}/time_series",
        params={
            "symbol": symbol,
            "interval": interval,
            "outputsize": outputsize,
            "apikey": TWELVE_DATA_API_KEY,
        },
        timeout=20,
    )

    response.raise_for_status()

    data = response.json()

    if "values" not in data:
        raise RuntimeError(data)

    candles = []

    for item in reversed(data["values"]):
        candles.append({
            "datetime": item["datetime"],
            "open": float(item["open"]),
            "high": float(item["high"]),
            "low": float(item["low"]),
            "close": float(item["close"]),
        })

    return candles
