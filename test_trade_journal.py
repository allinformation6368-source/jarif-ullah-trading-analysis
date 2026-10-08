from analysis.trade_journal import (
    create_trade_record,
    append_trade_record,
    summarize_journal,
)


def make_trade_plan():
    return {
        "status": "READY",
        "signal": "BUY",
        "entry": 100,
        "stop_loss": 95,
        "take_profit": 110,
        "risk": 5,
        "reward": 10,
        "risk_reward": 2,
        "position_size": 20,
        "risk_guard": "APPROVED",
        "entry_quality": "GOOD",
    }


def test_create_trade_record():
    record = create_trade_record(
        make_trade_plan(),
        market_regime="TRENDING_BULLISH",
        session="LONDON",
        timestamp="2026-10-07T10:30:00+00:00",
    )

    assert record["status"] == "RECORDED"
    assert record["signal"] == "BUY"
    assert record["entry"] == 100
    assert record["stop_loss"] == 95
    assert record["take_profit"] == 110
    assert record["market_regime"] == "TRENDING_BULLISH"
    assert record["session"] == "LONDON"


def test_reject_non_ready_plan():
    plan = make_trade_plan()
    plan["status"] = "WAIT"

    result = create_trade_record(plan)

    assert result["status"] == "REJECTED"


def test_reject_missing_field():
    plan = make_trade_plan()
    del plan["stop_loss"]

    result = create_trade_record(plan)

    assert result["status"] == "REJECTED"
    assert "Missing trade field" in result["reason"]


def test_append_trade_record():
    journal = []
    record = create_trade_record(make_trade_plan())

    result = append_trade_record(journal, record)

    assert result["status"] == "RECORDED"
    assert result["count"] == 1
    assert journal[0]["signal"] == "BUY"


def test_reject_invalid_record():
    journal = []

    result = append_trade_record(
        journal,
        {"status": "REJECTED"},
    )

    assert result["status"] == "REJECTED"
    assert len(journal) == 0


def test_summarize_journal():
    journal = []

    for signal in ("BUY", "BUY", "SELL"):
        plan = make_trade_plan()
        plan["signal"] = signal
        record = create_trade_record(plan)
        append_trade_record(journal, record)

    result = summarize_journal(journal)

    assert result["status"] == "VALID"
    assert result["total_trades"] == 3
    assert result["signals"]["BUY"] == 2
    assert result["signals"]["SELL"] == 1


def test_empty_journal_summary():
    result = summarize_journal([])

    assert result["status"] == "VALID"
    assert result["total_trades"] == 0
    assert result["signals"] == {}
