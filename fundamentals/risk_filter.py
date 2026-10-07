from datetime import datetime, timezone


def calculate_event_risk(events, symbol=None, now=None, window_minutes=60):
    now = now or datetime.now(timezone.utc)
    high = 0
    medium = 0
    low = 0
    upcoming = []

    for event in events:
        impact = str(event.get("impact", "LOW")).upper()
        event_time = event.get("datetime") or event.get("time_utc")
        affected_pairs = event.get("affected_pairs", [])

        if symbol and affected_pairs and symbol not in affected_pairs:
            continue

        if event_time:
            try:
                event_dt = datetime.fromisoformat(event_time.replace("Z", "+00:00"))
                minutes = abs((event_dt - now).total_seconds()) / 60

                if minutes <= window_minutes:
                    upcoming.append(event)
                    if impact == "HIGH":
                        high += 1
                    elif impact == "MEDIUM":
                        medium += 1
                    else:
                        low += 1
            except ValueError:
                pass

    if high > 0:
        risk = "HIGH"
    elif medium > 0:
        risk = "MEDIUM"
    elif low > 0:
        risk = "LOW"
    else:
        risk = "NONE"

    return {
        "risk": risk,
        "high_events": high,
        "medium_events": medium,
        "low_events": low,
        "upcoming_events": upcoming,
    }
