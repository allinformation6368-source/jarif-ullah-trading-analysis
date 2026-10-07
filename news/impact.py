HIGH_IMPACT_KEYWORDS = [
    "interest rate", "rate decision", "fomc", "ecb", "boe", "boj",
    "nonfarm payrolls", "nfp", "cpi", "pce", "gdp", "inflation",
    "unemployment", "fed", "central bank", "emergency", "war",
    "sanctions", "tariffs", "banking crisis"
]

MEDIUM_IMPACT_KEYWORDS = [
    "pmi", "retail sales", "jobless claims", "consumer confidence",
    "housing", "manufacturing", "services", "trade balance", "oil"
]


def detect_impact(text):
    text = text.lower()

    high = sum(1 for word in HIGH_IMPACT_KEYWORDS if word in text)
    medium = sum(1 for word in MEDIUM_IMPACT_KEYWORDS if word in text)

    if high > 0:
        level = "HIGH"
    elif medium > 0:
        level = "MEDIUM"
    else:
        level = "LOW"

    return {
        "impact": level,
        "high_matches": high,
        "medium_matches": medium,
    }
