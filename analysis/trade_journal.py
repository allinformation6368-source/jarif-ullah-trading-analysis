from datetime import datetime, timezone


REQUIRED_FIELDS = (
    "signal",
    "entry",
    "stop_loss",
    "take_profit",
    "risk",
    "reward",
    "risk_reward",
)


def create_trade_record(
    trade_plan,
    market_regime=None,
    session=None,
    timestamp=None,
):
    if not isinstance(trade_plan, dict):
        return {
            "status": "REJECTED",
            "reason": "Invalid trade plan",
        }

    if trade_plan.get("status") != "READY":
        return {
            "status": "REJECTED",
            "reason": "Trade plan is not ready",
        }

    for field in REQUIRED_FIELDS:
        if field not in trade_plan:
            return {
                "status": "REJECTED",
                "reason": f"Missing trade field: {field}",
            }

    if timestamp is None:
        timestamp = datetime.now(timezone.utc).isoformat()

    record = {
        "status": "RECORDED",
        "timestamp": timestamp,
        "signal": trade_plan["signal"],
        "entry": trade_plan["entry"],
        "stop_loss": trade_plan["stop_loss"],
        "take_profit": trade_plan["take_profit"],
        "risk": trade_plan["risk"],
        "reward": trade_plan["reward"],
        "risk_reward": trade_plan["risk_reward"],
    }

    optional_fields = (
        "sl_source",
        "account_balance",
        "risk_percent",
        "risk_amount",
        "position_size",
        "risk_guard",
        "entry_quality",
    )

    for field in optional_fields:
        if field in trade_plan:
            record[field] = trade_plan[field]

    if market_regime is not None:
        record["market_regime"] = market_regime

    if session is not None:
        record["session"] = session

    return record


def append_trade_record(journal, record):
    if not isinstance(journal, list):
        return {
            "status": "REJECTED",
            "reason": "Invalid journal",
        }

    if not isinstance(record, dict):
        return {
            "status": "REJECTED",
            "reason": "Invalid trade record",
        }

    if record.get("status") != "RECORDED":
        return {
            "status": "REJECTED",
            "reason": "Trade record is not valid",
        }

    journal.append(dict(record))

    return {
        "status": "RECORDED",
        "count": len(journal),
        "record": journal[-1],
    }


def summarize_journal(journal):
    if not isinstance(journal, list):
        return {
            "status": "REJECTED",
            "reason": "Invalid journal",
        }

    total = len(journal)

    signals = {}
    for record in journal:
        signal = record.get("signal", "UNKNOWN")
        signals[signal] = signals.get(signal, 0) + 1

    return {
        "status": "VALID",
        "total_trades": total,
        "signals": signals,
    }
