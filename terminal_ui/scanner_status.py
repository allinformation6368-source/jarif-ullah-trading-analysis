from __future__ import annotations


VALID_STATUS = {
    "ACTIVE",
    "PAUSED",
    "BUDGET_LIMIT",
}


def build_scanner_status(
    *,
    scanner_status,
    current_pair=None,
    next_pair=None,
    signal="WAIT",
    quality="LOW",
    confidence=0,
    setup_state="",
    credits_used=0,
    credits_remaining=800,
    planned_budget=750,
    safety_reserve=50,
    mode="PAPER",
):
    if scanner_status not in VALID_STATUS:
        scanner_status = "PAUSED"

    confidence = max(0, min(100, int(confidence)))

    return {
        "scanner_status": scanner_status,
        "current_pair": current_pair or "—",
        "next_pair": next_pair or "—",
        "signal": signal,
        "quality": quality,
        "confidence": confidence,
        "setup_state": setup_state or "—",
        "credits_used": max(0, int(credits_used)),
        "credits_remaining": max(0, int(credits_remaining)),
        "planned_budget": max(0, int(planned_budget)),
        "safety_reserve": max(0, int(safety_reserve)),
        "mode": mode,
        "live_execution": False,
    }


def format_scanner_status(status):
    return (
        f"SCANNER: {status['scanner_status']}\n"
        f"PAIR: {status['current_pair']}\n"
        f"NEXT: {status['next_pair']}\n"
        f"SIGNAL: {status['signal']}\n"
        f"QUALITY: {status['quality']}\n"
        f"CONFIDENCE: {status['confidence']}/100\n"
        f"SETUP: {status['setup_state']}\n"
        f"CREDITS: {status['credits_used']}/"
        f"{status['planned_budget']} "
        f"(remaining {status['credits_remaining']}, "
        f"reserve {status['safety_reserve']})\n"
        f"MODE: {status['mode']}\n"
        f"LIVE EXECUTION: "
        f"{'ON' if status['live_execution'] else 'OFF'}"
    )
