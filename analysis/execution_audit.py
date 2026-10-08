from datetime import datetime, timezone
import json
from pathlib import Path


DEFAULT_AUDIT_FILE = Path("logs/execution_audit.jsonl")


def create_execution_audit(
    result,
    order=None,
    mode=None,
):
    if not isinstance(result, dict):
        return {
            "status": "REJECTED",
            "reason": "Invalid execution result",
        }

    if order is not None and not isinstance(order, dict):
        return {
            "status": "REJECTED",
            "reason": "Invalid order",
        }

    timestamp = datetime.now(timezone.utc).isoformat()

    return {
        "timestamp": timestamp,
        "execution_status": result.get("status"),
        "mode": result.get("mode", mode),
        "signal": (
            order.get("signal")
            if isinstance(order, dict)
            else result.get("signal")
        ),
        "entry": (
            order.get("entry")
            if isinstance(order, dict)
            else result.get("entry")
        ),
        "stop_loss": (
            order.get("stop_loss")
            if isinstance(order, dict)
            else result.get("stop_loss")
        ),
        "take_profit": (
            order.get("take_profit")
            if isinstance(order, dict)
            else result.get("take_profit")
        ),
        "account_balance": result.get("account_balance"),
        "risk_percent": result.get("risk_percent"),
        "risk_reward": result.get("risk_reward"),
        "reason": result.get("reason"),
    }


def is_execution_successful(audit):
    if not isinstance(audit, dict):
        return False

    return audit.get("execution_status") in (
        "PAPER_ACCEPTED",
    )


def persist_execution_audit(
    audit,
    audit_file=DEFAULT_AUDIT_FILE,
):
    if not isinstance(audit, dict):
        return {
            "status": "REJECTED",
            "reason": "Invalid audit record",
        }

    audit_file = Path(audit_file)
    audit_file.parent.mkdir(parents=True, exist_ok=True)

    with audit_file.open("a", encoding="utf-8") as file:
        file.write(json.dumps(audit, separators=(",", ":")) + "\n")

    return {
        "status": "SAVED",
        "path": str(audit_file),
    }


def read_execution_audits(
    audit_file=DEFAULT_AUDIT_FILE,
):
    audit_file = Path(audit_file)

    if not audit_file.exists():
        return []

    records = []

    with audit_file.open("r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if line:
                records.append(json.loads(line))

    return records
