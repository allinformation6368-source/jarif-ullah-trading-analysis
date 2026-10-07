from fundamentals.asset_mapping import get_affected_assets, get_affected_pairs


def normalize_news_item(title, description="", source="unknown", published_at=None):
    return {
        "title": title,
        "description": description,
        "source": source,
        "published_at": published_at,
    }


def normalize_events(events):
    normalized = []

    for event in events:
        title = event.get("title") or event.get("name") or ""

        normalized.append({
            "title": title,
            "currency": event.get("currency", ""),
            "impact": str(event.get("impact", "LOW")).upper(),
            "datetime": event.get("datetime") or event.get("time_utc"),
            "actual": event.get("actual"),
            "forecast": event.get("forecast") or event.get("consensus"),
            "previous": event.get("previous") or event.get("prior"),
            "affected_assets": get_affected_assets(title),
            "affected_pairs": get_affected_pairs(title),
            "source_url": event.get("url"),
        })

    return normalized
