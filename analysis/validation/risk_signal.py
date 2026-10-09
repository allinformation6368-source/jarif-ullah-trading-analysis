from __future__ import annotations


VALID_DECISIONS = {"BUY", "SELL", "WAIT", "INVALIDATED"}


def validate_risk_signal(
    signal,
    risk_result=None,
    position_result=None,
    guard_result=None,
):
    """
    Connect validated signal output with existing risk components.

    Analysis/validation only.
    No order, execution, broker, or live-trading actions.
    """

    if not isinstance(signal, dict):
        raise TypeError("signal must be a dict")

    decision = signal.get("decision", "WAIT")

    if decision not in VALID_DECISIONS:
        return {
            "decision": "WAIT",
            "valid": False,
            "reason": "INVALID_SIGNAL_DECISION",
            "risk_valid": False,
            "position_valid": False,
            "guard_valid": False,
        }

    if decision in {"WAIT", "INVALIDATED"}:
        return {
            "decision": decision,
            "valid": True,
            "reason": "NO_RISK_ACTION",
            "risk_valid": True,
            "position_valid": False,
            "guard_valid": True,
        }

    risk_valid = True
    position_valid = True
    guard_valid = True

    if isinstance(risk_result, dict):
        if risk_result.get("valid") is False:
            risk_valid = False
        if risk_result.get("status") in {"INVALID", "FAILED", "ERROR"}:
            risk_valid = False

    if isinstance(position_result, dict):
        if position_result.get("valid") is False:
            position_valid = False
        if position_result.get("status") in {"INVALID", "FAILED", "ERROR"}:
            position_valid = False

    if isinstance(guard_result, dict):
        if guard_result.get("valid") is False:
            guard_valid = False
        if guard_result.get("allowed") is False:
            guard_valid = False
        if guard_result.get("status") in {"BLOCKED", "INVALID", "FAILED", "ERROR"}:
            guard_valid = False

    if not risk_valid:
        return {
            "decision": "WAIT",
            "valid": False,
            "reason": "RISK_INVALID",
            "risk_valid": False,
            "position_valid": position_valid,
            "guard_valid": guard_valid,
        }

    if not position_valid:
        return {
            "decision": "WAIT",
            "valid": False,
            "reason": "POSITION_INVALID",
            "risk_valid": True,
            "position_valid": False,
            "guard_valid": guard_valid,
        }

    if not guard_valid:
        return {
            "decision": "WAIT",
            "valid": False,
            "reason": "RISK_GUARD_BLOCKED",
            "risk_valid": True,
            "position_valid": position_valid,
            "guard_valid": False,
        }

    return {
        "decision": decision,
        "valid": True,
        "reason": "RISK_VALIDATED",
        "risk_valid": True,
        "position_valid": True,
        "guard_valid": True,
    }
