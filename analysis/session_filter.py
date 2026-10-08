from datetime import datetime, timezone


SESSION_WINDOWS = {
    "ASIA": (0, 8),
    "LONDON": (8, 13),
    "NEW_YORK": (13, 21),
    "OFF_SESSION": (21, 24),
}


def detect_session(candles):
    if not candles:
        return {
            "status": "WAIT",
            "session": "UNKNOWN",
            "reason": "No candles",
        }

    last_candle = candles[-1]

    if not isinstance(last_candle, dict):
        return {
            "status": "WAIT",
            "session": "UNKNOWN",
            "reason": "Invalid candle",
        }

    timestamp = last_candle.get("datetime")

    if not timestamp:
        return {
            "status": "WAIT",
            "session": "UNKNOWN",
            "reason": "Missing datetime",
        }

    try:
        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))

        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)

        hour = dt.astimezone(timezone.utc).hour
    except (ValueError, TypeError):
        return {
            "status": "WAIT",
            "session": "UNKNOWN",
            "reason": "Invalid datetime",
        }

    for session, (start, end) in SESSION_WINDOWS.items():
        if start <= hour < end:
            return {
                "status": "VALID",
                "session": session,
                "hour_utc": hour,
            }

    return {
        "status": "VALID",
        "session": "OFF_SESSION",
        "hour_utc": hour,
    }


def validate_session(session_data, allowed_sessions=None):
    if not isinstance(session_data, dict):
        return {
            "status": "REJECTED",
            "reason": "Invalid session data",
        }

    if session_data.get("status") != "VALID":
        return {
            "status": "REJECTED",
            "reason": "Invalid session",
        }

    session = session_data.get("session")

    if allowed_sessions is None:
        allowed_sessions = (
            "ASIA",
            "LONDON",
            "NEW_YORK",
        )

    if session not in allowed_sessions:
        return {
            "status": "BLOCKED",
            "session": session,
            "reason": "Session not allowed",
        }

    return {
        "status": "APPROVED",
        "session": session,
    }
