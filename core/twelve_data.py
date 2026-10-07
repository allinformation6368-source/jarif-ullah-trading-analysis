import time
import requests

from config.settings import TWELVE_DATA_API_KEY

BASE_URL = "https://api.twelvedata.com"


def get_price(symbol, retries=3):
    for attempt in range(retries):
        try:
            response = requests.get(
                f"{BASE_URL}/price",
                params={
                    "symbol": symbol,
                    "apikey": TWELVE_DATA_API_KEY,
                },
                timeout=15,
            )

            if response.status_code == 429:
                wait = min(5 * (attempt + 1), 15)
                time.sleep(wait)
                continue

            response.raise_for_status()

            data = response.json()

            if "price" not in data:
                raise RuntimeError(data)

            return float(data["price"])

        except requests.RequestException:
            if attempt == retries - 1:
                raise
            time.sleep(2 * (attempt + 1))

    raise RuntimeError(f"Rate limit or request failed for {symbol}")
