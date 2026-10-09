from __future__ import annotations

from time import time


VALID_STATES = {
    "NEW",
    "ACTIVE",
    "INVALIDATED",
    "EXPIRED",
}


def evaluate_setup_lifecycle(
    *,
    setup_id,
    decision,
    candle_id,
    now=None,
    expires_at=None,
    previous_state=None,
):
    """
    Pure local setup lifecycle evaluator.

    No API calls.
    No execution.
    """

    if not setup_id:
        raise ValueError("setup_id is required")

    if now is None:
        now = time()

    previous_state = previous_state or "NEW"

    if previous_state not in VALID_STATES:
        previous_state = "NEW"

    if decision == "INVALIDATED":
        state = "INVALIDATED"
        reason = "SIGNAL_INVALIDATED"

    elif expires_at is not None and now >= expires_at:
        state = "EXPIRED"
        reason = "SETUP_EXPIRED"

    elif decision in {"BUY", "SELL"}:
        state = "ACTIVE"
        reason = (
            "SETUP_CONFIRMED"
            if previous_state in {"NEW", "INVALIDATED", "EXPIRED"}
            else "SETUP_STILL_ACTIVE"
        )

    else:
        state = previous_state
        reason = "NO_ACTIVE_ENTRY_SIGNAL"

        if state == "NEW":
            state = "ACTIVE"

    return {
        "setup_id": setup_id,
        "state": state,
        "reason": reason,
        "decision": decision,
        "candle_id": candle_id,
        "timestamp": now,
        "expired": state == "EXPIRED",
        "invalidated": state == "INVALIDATED",
        "active": state == "ACTIVE",
    }
