def calculate_premium_discount(candles):
    if not candles:
        return None

    range_high = max(candle["high"] for candle in candles)
    range_low = min(candle["low"] for candle in candles)

    equilibrium = (range_high + range_low) / 2
    current_price = candles[-1]["close"]

    if current_price > equilibrium:
        zone = "PREMIUM"
    elif current_price < equilibrium:
        zone = "DISCOUNT"
    else:
        zone = "EQUILIBRIUM"

    return {
        "range_high": range_high,
        "range_low": range_low,
        "equilibrium": equilibrium,
        "current_price": current_price,
        "zone": zone,
    }
