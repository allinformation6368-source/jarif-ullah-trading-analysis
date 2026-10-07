import requests

API_URL = "https://www.financecalendar.com/wp-json/fc/v1/calendar"


def get_calendar_events(start_date, end_date, impact=None, limit=50):
    params = {
        "from": start_date,
        "to": end_date,
        "limit": limit,
    }

    if impact:
        params["impact"] = impact

    response = requests.get(API_URL, params=params, timeout=15)
    response.raise_for_status()
    data = response.json()

    return data.get("events", [])
