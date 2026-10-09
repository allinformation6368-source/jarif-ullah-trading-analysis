from __future__ import annotations


VALID_DECISIONS = {"BUY", "SELL", "WAIT", "INVALIDATED"}
VALID_QUALITIES = {"HIGH", "MEDIUM", "LOW"}


def _num(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def evaluate_confidence(
    *,
    decision,
    confluence=None,
    mtf_validation=None,
    risk_validation=None,
):
    """
    Local confidence/quality gate.

    This does not create a signal.
    It only grades an already validated candidate.

    No API calls.
    No execution.
    """

    if decision not in VALID_DECISIONS:
        decision = "WAIT"

    confluence = confluence if isinstance(confluence, dict) else {}
    mtf_validation = (
        mtf_validation if isinstance(mtf_validation, dict) else {}
    )
    risk_validation = (
        risk_validation if isinstance(risk_validation, dict) else None
    )

    if decision in {"WAIT", "INVALIDATED"}:
        return {
            "decision": decision,
            "confidence": 0,
            "quality": "LOW",
            "qualified": False,
            "reason": "NO_ACTIVE_SIGNAL",
            "components": {},
        }

    score = 0.0
    components = {}

    # Confluence: max contribution 40
    confluence_score = _num(confluence.get("score", 0))
    confluence_points = min(abs(confluence_score) * 5.0, 40.0)
    components["confluence"] = confluence_points
    score += confluence_points

    # MTF alignment: 30
    aligned = bool(mtf_validation.get("aligned", False))
    contradiction = bool(mtf_validation.get("contradiction", False))

    mtf_points = 30.0 if aligned and not contradiction else 0.0
    components["mtf_alignment"] = mtf_points
    score += mtf_points

    # Risk validation: 30
    risk_valid = bool(risk_validation.get("valid", False))
    risk_points = 30.0 if risk_valid else 0.0
    components["risk_validation"] = risk_points
    score += risk_points

    score = min(max(score, 0.0), 100.0)

    if contradiction:
        quality = "LOW"
        qualified = False
        reason = "MTF_CONTRADICTION"
    elif not risk_valid:
        quality = "LOW"
        qualified = False
        reason = "RISK_NOT_VALIDATED"
    elif score >= 80:
        quality = "HIGH"
        qualified = True
        reason = "HIGH_CONFIDENCE"
    elif score >= 60:
        quality = "MEDIUM"
        qualified = True
        reason = "MEDIUM_CONFIDENCE"
    else:
        quality = "LOW"
        qualified = False
        reason = "LOW_CONFIDENCE"

    return {
        "decision": decision,
        "confidence": round(score, 2),
        "quality": quality,
        "qualified": qualified,
        "reason": reason,
        "components": components,
    }
