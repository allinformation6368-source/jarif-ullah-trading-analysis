from __future__ import annotations


VALID_DECISIONS = {"BUY", "SELL", "WAIT", "INVALIDATED"}


def _safe_score(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def evaluate_candidate(
    *,
    pair,
    timeframe_results,
    mtf_validation,
    confluence=None,
    risk_validation=None,
    setup_persistence=None,
):
    """
    Local scanner intelligence layer.

    Responsibilities:
    - candidate filtering
    - MTF contradiction handling
    - confluence awareness
    - risk-validation awareness
    - setup persistence metadata

    No provider/API calls.
    No execution.
    """

    if not pair:
        raise ValueError("pair is required")

    if not isinstance(timeframe_results, dict):
        raise TypeError("timeframe_results must be a dict")

    if not isinstance(mtf_validation, dict):
        raise TypeError("mtf_validation must be a dict")

    decision = mtf_validation.get("decision", "WAIT")

    if decision not in VALID_DECISIONS:
        decision = "WAIT"

    contradiction = bool(
        mtf_validation.get("contradiction", False)
    )

    aligned = bool(
        mtf_validation.get("aligned", False)
    )

    directions = mtf_validation.get("directions", {})

    if not isinstance(directions, dict):
        directions = {}

    score = 0.0

    if isinstance(confluence, dict):
        score += _safe_score(confluence.get("score", 0))

        if confluence.get("decision") == "INVALIDATED":
            contradiction = True

    if contradiction:
        final_decision = "INVALIDATED"
        reason = "CONTRADICTION"
    elif decision in {"BUY", "SELL"} and aligned:
        final_decision = decision
        reason = "CANDIDATE_ALIGNED"
    else:
        final_decision = "WAIT"
        reason = "INSUFFICIENT_CONFLUENCE"

    risk_checked = risk_validation is not None
    risk_valid = True

    if isinstance(risk_validation, dict):
        risk_valid = bool(risk_validation.get("valid", False))

    if final_decision in {"BUY", "SELL"}:
        if not risk_checked:
            final_decision = "WAIT"
            reason = "RISK_NOT_VALIDATED"
        elif not risk_valid:
            final_decision = "WAIT"
            reason = "RISK_BLOCKED"

    setup_key = None

    if final_decision in {"BUY", "SELL"}:
        setup_key = f"{pair}|{final_decision}"

    persisted = False

    if setup_persistence is not None and setup_key:
        observe = getattr(setup_persistence, "observe", None)

        if callable(observe):
            observe(
                pair=pair,
                mode="scanner",
                setup_id=setup_key,
                candle_id=None,
                metadata={
                    "decision": final_decision,
                    "score": score,
                    "directions": directions,
                },
            )
            persisted = True

    return {
        "pair": pair,
        "decision": final_decision,
        "reason": reason,
        "candidate": final_decision in {"BUY", "SELL"},
        "aligned": aligned,
        "contradiction": contradiction,
        "score": score,
        "directions": directions,
        "risk_checked": risk_checked,
        "risk_valid": risk_valid,
        "setup_key": setup_key,
        "setup_persisted": persisted,
    }
