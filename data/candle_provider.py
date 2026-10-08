from datetime import datetime


REQUIRED_CANDLE_FIELDS = (
    "datetime",
    "open",
    "high",
    "low",
    "close",
)


def validate_candle(candle):
    if not isinstance(candle, dict):
        return {
            "status": "REJECTED",
            "reason": "Invalid candle",
        }

    for field in REQUIRED_CANDLE_FIELDS:
        if field not in candle:
            return {
                "status": "REJECTED",
                "reason": f"Missing candle field: {field}",
            }

    try:
        open_price = float(candle["open"])
        high_price = float(candle["high"])
        low_price = float(candle["low"])
        close_price = float(candle["close"])
    except (TypeError, ValueError):
        return {
            "status": "REJECTED",
            "reason": "Invalid candle price",
        }

    if min(
        open_price,
        high_price,
        low_price,
        close_price,
    ) <= 0:
        return {
            "status": "REJECTED",
            "reason": "Candle prices must be positive",
        }

    if high_price < max(open_price, close_price):
        return {
            "status": "REJECTED",
            "reason": "Invalid candle high",
        }

    if low_price > min(open_price, close_price):
        return {
            "status": "REJECTED",
            "reason": "Invalid candle low",
        }

    if high_price < low_price:
        return {
            "status": "REJECTED",
            "reason": "Invalid candle range",
        }

    try:
        datetime.fromisoformat(
            str(candle["datetime"]).replace("Z", "+00:00")
        )
    except (TypeError, ValueError):
        return {
            "status": "REJECTED",
            "reason": "Invalid candle datetime",
        }

    return {
        "status": "VALID",
    }


def normalize_candle(candle):
    validation = validate_candle(candle)

    if validation["status"] != "VALID":
        return validation

    return {
        "status": "VALID",
        "candle": {
            "datetime": str(candle["datetime"]),
            "open": float(candle["open"]),
            "high": float(candle["high"]),
            "low": float(candle["low"]),
            "close": float(candle["close"]),
            "volume": (
                float(candle["volume"])
                if candle.get("volume") is not None
                else None
            ),
        },
    }


def normalize_candles(candles):
    if not isinstance(candles, list):
        return {
            "status": "REJECTED",
            "reason": "Candles must be a list",
        }

    normalized = []

    for candle in candles:
        result = normalize_candle(candle)

        if result["status"] != "VALID":
            return result

        normalized.append(result["candle"])

    return {
        "status": "VALID",
        "candles": normalized,
    }
