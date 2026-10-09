from __future__ import annotations

from .confidence import evaluate_confidence
from .intelligence import evaluate_candidate
from .setup_lifecycle import evaluate_setup_lifecycle


def run_scanner_intelligence(
    *,
    pair,
    timeframe_results,
    mtf_validation,
    confluence,
    risk_validation,
    candle_id,
    previous_state=None,
    now=None,
    expires_at=None,
):
    """
    End-to-end local scanner intelligence pipeline.

    Provider/API access is intentionally outside this function.
    """

    candidate = evaluate_candidate(
        pair=pair,
        timeframe_results=timeframe_results,
        mtf_validation=mtf_validation,
        confluence=confluence,
        risk_validation=risk_validation,
    )

    confidence = evaluate_confidence(
        decision=candidate["decision"],
        confluence=confluence,
        mtf_validation=mtf_validation,
        risk_validation=risk_validation,
    )

    lifecycle = evaluate_setup_lifecycle(
        setup_id=candidate["setup_key"] or f"{pair}|WAIT",
        decision=(
            candidate["decision"]
            if confidence["qualified"]
            else "WAIT"
            if candidate["decision"] in {"BUY", "SELL"}
            else candidate["decision"]
        ),
        candle_id=candle_id,
        previous_state=previous_state,
        now=now,
        expires_at=expires_at,
    )

    return {
        "pair": pair,
        "decision": candidate["decision"],
        "candidate": candidate["candidate"],
        "reason": candidate["reason"],
        "confidence": confidence["confidence"],
        "quality": confidence["quality"],
        "qualified": confidence["qualified"],
        "confidence_reason": confidence["reason"],
        "confidence_components": confidence["components"],
        "setup_id": lifecycle["setup_id"],
        "setup_state": lifecycle["state"],
        "setup_reason": lifecycle["reason"],
        "candle_id": candle_id,
        "risk_checked": candidate["risk_checked"],
        "risk_valid": candidate["risk_valid"],
        "contradiction": candidate["contradiction"],
        "directions": candidate["directions"],
    }
