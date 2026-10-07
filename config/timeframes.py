TRADING_MODES = {
    "scalping": {
        "primary": ["1min", "5min"],
        "confirmation": ["5min", "15min"],
        "bias": ["15min", "1h"],
    },
    "intraday": {
        "primary": ["5min", "15min"],
        "confirmation": ["15min", "1h"],
        "bias": ["1h", "4h"],
    },
    "swing": {
        "primary": ["4h", "1day"],
        "confirmation": ["1day"],
        "bias": ["1day", "1week"],
    },
}
