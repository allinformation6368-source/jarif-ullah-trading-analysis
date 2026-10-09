from analysis.indicators.local_indicators import analyze_local
from analysis.market_structure import analyze_market_structure


def _direction(value):
    if value in ("BULLISH", "BUY"):
        return "BULLISH"
    if value in ("BEARISH", "SELL"):
        return "BEARISH"
    return "NEUTRAL"


def _score_component(score, direction, weight, reason):
    return {
        "direction": direction,
        "weight": weight,
        "score": score,
        "reason": reason,
    }


def _indicator_components(indicators):
    components = []

    trend = _direction(indicators.get("trend"))

    if trend == "BULLISH":
        components.append(
            _score_component(1, "BULLISH", 1, "local trend bullish")
        )
    elif trend == "BEARISH":
        components.append(
            _score_component(-1, "BEARISH", 1, "local trend bearish")
        )

    rsi = indicators.get("rsi_14")

    if rsi is not None:
        if rsi < 35:
            components.append(
                _score_component(1, "BULLISH", 1, "RSI oversold")
            )
        elif rsi > 65:
            components.append(
                _score_component(-1, "BEARISH", 1, "RSI overbought")
            )

    macd = indicators.get("macd")

    if macd:
        histogram = macd.get("histogram")

        if histogram is not None:
            if histogram > 0:
                components.append(
                    _score_component(
                        1,
                        "BULLISH",
                        1,
                        "MACD histogram positive",
                    )
                )
            elif histogram < 0:
                components.append(
                    _score_component(
                        -1,
                        "BEARISH",
                        1,
                        "MACD histogram negative",
                    )
                )

    return components


def _structure_components(structure):
    components = []

    bias = _direction(structure.get("structure"))

    if bias == "BULLISH":
        components.append(
            _score_component(
                2,
                "BULLISH",
                2,
                "market structure bullish",
            )
        )
    elif bias == "BEARISH":
        components.append(
            _score_component(
                -2,
                "BEARISH",
                2,
                "market structure bearish",
            )
        )

    sweep = structure.get("sweep") or {}

    if sweep.get("sweep"):
        direction = _direction(sweep.get("direction"))

        if direction == "BULLISH":
            components.append(
                _score_component(
                    2,
                    "BULLISH",
                    2,
                    "bullish liquidity sweep",
                )
            )
        elif direction == "BEARISH":
            components.append(
                _score_component(
                    -2,
                    "BEARISH",
                    2,
                    "bearish liquidity sweep",
                )
            )

    mss = structure.get("mss") or {}

    if mss.get("mss"):
        direction = _direction(mss.get("direction"))

        if direction == "BULLISH":
            components.append(
                _score_component(
                    2,
                    "BULLISH",
                    2,
                    "bullish market structure shift",
                )
            )
        elif direction == "BEARISH":
            components.append(
                _score_component(
                    -2,
                    "BEARISH",
                    2,
                    "bearish market structure shift",
                )
            )

    return components


def _decision(score, bullish, bearish):
    if bullish and bearish:
        return "INVALIDATED"

    if score >= 4:
        return "BUY"

    if score <= -4:
        return "SELL"

    return "WAIT"


def analyze_confluence(candles):
    indicators = analyze_local(candles)
    structure = analyze_market_structure(candles)

    components = (
        _indicator_components(indicators)
        + _structure_components(structure)
    )

    score = sum(component["score"] for component in components)

    bullish = any(
        component["direction"] == "BULLISH"
        for component in components
    )

    bearish = any(
        component["direction"] == "BEARISH"
        for component in components
    )

    bullish_score = sum(
        component["score"]
        for component in components
        if component["direction"] == "BULLISH"
    )

    bearish_score = abs(
        sum(
            component["score"]
            for component in components
            if component["direction"] == "BEARISH"
        )
    )

    decision = _decision(score, bullish, bearish)

    return {
        "decision": decision,
        "score": score,
        "bullish_score": bullish_score,
        "bearish_score": bearish_score,
        "contradiction": bullish and bearish,
        "components": components,
        "indicators": indicators,
        "structure": structure,
    }
