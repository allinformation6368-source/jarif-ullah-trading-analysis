import time

from config.assets import ALL_PAIRS
from core.twelve_data import get_price

DEFAULT_SYMBOLS = ALL_PAIRS


def get_market_snapshot(symbols=None):
    symbols = symbols or DEFAULT_SYMBOLS
    snapshot = {}

    for symbol in symbols:
        try:
            snapshot[symbol] = {
                "price": get_price(symbol),
                "status": "OK"
            }
        except Exception as exc:
            snapshot[symbol] = {
                "price": None,
                "status": "ERROR",
                "error": str(exc)
            }
        time.sleep(0.5)

    return snapshot
