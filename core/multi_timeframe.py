from config.timeframes import TRADING_MODES
from core.candles import get_candles


def get_mode_data(symbol, mode, outputsize=100):
    if mode not in TRADING_MODES:
        raise ValueError(
            f"Unknown mode: {mode}. "
            f"Available: {', '.join(TRADING_MODES)}"
        )

    config = TRADING_MODES[mode]

    timeframes = (
        config["primary"]
        + config["confirmation"]
        + config["bias"]
    )

    unique_timeframes = list(dict.fromkeys(timeframes))

    data = {}

    for timeframe in unique_timeframes:
        data[timeframe] = get_candles(
            symbol,
            interval=timeframe,
            outputsize=outputsize,
        )

    return data
