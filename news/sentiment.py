def classify_sentiment(text):
    text = text.lower()

    bullish_words = [
        "hawkish", "rate hike", "strong growth", "beats expectations",
        "positive", "surge", "rally", "strong jobs", "higher yields"
    ]
    bearish_words = [
        "dovish", "rate cut", "weak growth", "misses expectations",
        "negative", "plunge", "recession", "weak jobs", "lower yields"
    ]

    bullish = sum(1 for word in bullish_words if word in text)
    bearish = sum(1 for word in bearish_words if word in text)

    if bullish > bearish:
        sentiment = "BULLISH"
    elif bearish > bullish:
        sentiment = "BEARISH"
    else:
        sentiment = "NEUTRAL"

    return {
        "sentiment": sentiment,
        "bullish_score": bullish,
        "bearish_score": bearish,
    }
