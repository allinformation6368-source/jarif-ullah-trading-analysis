from config.timeframes import TRADING_MODES


def required_timeframes(mode):
    if mode not in TRADING_MODES:
        raise ValueError(f"Unknown trading mode: {mode}")

    config = TRADING_MODES[mode]

    ordered = []
    for group in ("primary", "confirmation", "bias"):
        for timeframe in config[group]:
            if timeframe not in ordered:
                ordered.append(timeframe)

    return tuple(ordered)


def unique_timeframes(*modes):
    result = []

    for mode in modes:
        for timeframe in required_timeframes(mode):
            if timeframe not in result:
                result.append(timeframe)

    return tuple(result)


def screening_timeframes(mode):
    required = required_timeframes(mode)

    # Cheap first-pass: primary timeframes only.
    config = TRADING_MODES[mode]

    result = []
    for timeframe in config["primary"]:
        if timeframe not in result:
            result.append(timeframe)

    return tuple(result)


def deeper_timeframes(mode):
    required = required_timeframes(mode)
    screening = set(screening_timeframes(mode))

    return tuple(tf for tf in required if tf not in screening)
