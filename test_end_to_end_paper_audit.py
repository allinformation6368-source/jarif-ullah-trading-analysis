from analysis.execution_audit import (
    persist_execution_audit,
    query_execution_audits,
    summarize_execution_audits,
)
from analysis.live_paper import run_live_paper_analysis


def _redirect_audit_persistence(monkeypatch, audit_file):
    def persist_to_test_file(audit, **kwargs):
        return persist_execution_audit(
            audit,
            audit_file=audit_file,
        )

    monkeypatch.setattr(
        "analysis.execution_gateway.persist_execution_audit",
        persist_to_test_file,
    )


def test_full_paper_execution_audit_chain(monkeypatch, tmp_path):
    audit_file = tmp_path / "execution_audit.jsonl"

    def fake_analyze(**kwargs):
        return {
            "status": "VALID",
            "symbol": kwargs["symbol"],
            "mode": kwargs["mode"],
            "analysis": {
                "paper_order": {
                    "signal": "BUY",
                    "entry": 100.0,
                    "stop_loss": 95.0,
                    "take_profit": 110.0,
                }
            },
        }

    monkeypatch.setattr(
        "analysis.live_paper.analyze_live_market",
        fake_analyze,
    )
    _redirect_audit_persistence(monkeypatch, audit_file)

    result = run_live_paper_analysis(
        symbol="BTC/USD",
        mode="scalping",
        account_balance=10000,
        risk_percent=1.0,
        outputsize=100,
    )

    assert result["status"] == "PAPER_ACCEPTED"
    assert result["execution"]["status"] == "PAPER_ACCEPTED"

    records = query_execution_audits(
        execution_status="PAPER_ACCEPTED",
        signal="BUY",
        mode="PAPER",
        limit=10,
        audit_file=audit_file,
    )

    assert len(records) == 1
    assert records[0]["execution_status"] == "PAPER_ACCEPTED"
    assert records[0]["signal"] == "BUY"
    assert records[0]["mode"] == "PAPER"

    summary = summarize_execution_audits(
        audit_file=audit_file,
    )

    assert summary["total"] == 1
    assert summary["accepted"] == 1
    assert summary["rejected"] == 0
    assert summary["buy"] == 1
    assert summary["paper"] == 1
    assert summary["live"] == 0


def test_full_chain_does_not_create_live_execution(monkeypatch, tmp_path):
    audit_file = tmp_path / "execution_audit.jsonl"

    def fake_analyze(**kwargs):
        return {
            "status": "VALID",
            "symbol": kwargs["symbol"],
            "mode": kwargs["mode"],
            "analysis": {
                "paper_order": {
                    "signal": "SELL",
                    "entry": 200.0,
                    "stop_loss": 205.0,
                    "take_profit": 190.0,
                }
            },
        }

    monkeypatch.setattr(
        "analysis.live_paper.analyze_live_market",
        fake_analyze,
    )
    _redirect_audit_persistence(monkeypatch, audit_file)

    result = run_live_paper_analysis(
        symbol="ETH/USD",
        mode="intraday",
    )

    assert result["status"] == "PAPER_ACCEPTED"

    live_records = query_execution_audits(
        mode="LIVE",
        audit_file=audit_file,
    )

    assert live_records == []

    paper_records = query_execution_audits(
        mode="PAPER",
        audit_file=audit_file,
    )

    assert len(paper_records) == 1
    assert paper_records[0]["signal"] == "SELL"


def test_full_chain_audit_rejection_query(monkeypatch, tmp_path):
    audit_file = tmp_path / "execution_audit.jsonl"

    def fake_analyze(**kwargs):
        return {
            "status": "VALID",
            "symbol": kwargs["symbol"],
            "mode": kwargs["mode"],
            "analysis": {
                "paper_order": {
                    "signal": "INVALID",
                    "entry": 100.0,
                    "stop_loss": 95.0,
                    "take_profit": 110.0,
                }
            },
        }

    monkeypatch.setattr(
        "analysis.live_paper.analyze_live_market",
        fake_analyze,
    )
    _redirect_audit_persistence(monkeypatch, audit_file)

    result = run_live_paper_analysis(
        symbol="BTC/USD",
        mode="scalping",
    )

    assert result["status"] != "PAPER_ACCEPTED"

    summary = summarize_execution_audits(
        audit_file=audit_file,
    )

    assert summary["total"] == 1
    assert summary["rejected"] == 1
    assert summary["accepted"] == 0
    assert summary["paper"] == 1
