from analysis.live_paper_audit import run_live_paper_with_audit


def test_live_paper_with_audit(monkeypatch, tmp_path):
    audit_file = tmp_path / "execution_audit.jsonl"

    def fake_run(**kwargs):
        return {
            "status": "PAPER_ACCEPTED",
            "symbol": kwargs["symbol"],
            "mode": kwargs["mode"],
            "execution": {
                "status": "PAPER_ACCEPTED",
                "signal": "BUY",
            },
            "analysis": {
                "decision": {
                    "decision": "ENTRY_READY",
                    "signal": "BUY",
                }
            },
        }

    def fake_query(**kwargs):
        assert kwargs["execution_status"] == "PAPER_ACCEPTED"
        assert kwargs["mode"] == "PAPER"
        assert kwargs["limit"] == 1
        return [
            {
                "execution_status": "PAPER_ACCEPTED",
                "signal": "BUY",
                "mode": "PAPER",
            }
        ]

    def fake_summary(**kwargs):
        return {
            "total": 1,
            "accepted": 1,
            "rejected": 0,
            "buy": 1,
            "sell": 0,
            "paper": 1,
            "live": 0,
            "rejection_reasons": {},
        }

    monkeypatch.setattr(
        "analysis.live_paper_audit.run_live_paper_analysis",
        fake_run,
    )
    monkeypatch.setattr(
        "analysis.live_paper_audit.query_execution_audits",
        fake_query,
    )
    monkeypatch.setattr(
        "analysis.live_paper_audit.summarize_execution_audits",
        fake_summary,
    )

    result = run_live_paper_with_audit(
        symbol="BTC/USD",
        mode="scalping",
        audit_file=audit_file,
    )

    assert result["status"] == "PAPER_ACCEPTED"
    assert result["symbol"] == "BTC/USD"
    assert result["mode"] == "scalping"
    assert result["audit"]["latest"][0]["signal"] == "BUY"
    assert result["audit"]["summary"]["accepted"] == 1


def test_live_paper_with_audit_no_trade(monkeypatch, tmp_path):
    audit_file = tmp_path / "execution_audit.jsonl"

    def fake_run(**kwargs):
        return {
            "status": "NO_TRADE",
            "symbol": kwargs["symbol"],
            "mode": kwargs["mode"],
            "execution": None,
        }

    monkeypatch.setattr(
        "analysis.live_paper_audit.run_live_paper_analysis",
        fake_run,
    )
    monkeypatch.setattr(
        "analysis.live_paper_audit.query_execution_audits",
        lambda **kwargs: [],
    )
    monkeypatch.setattr(
        "analysis.live_paper_audit.summarize_execution_audits",
        lambda **kwargs: {
            "total": 0,
            "accepted": 0,
            "rejected": 0,
            "buy": 0,
            "sell": 0,
            "paper": 0,
            "live": 0,
            "rejection_reasons": {},
        },
    )

    result = run_live_paper_with_audit(
        symbol="BTC/USD",
        mode="scalping",
        audit_file=audit_file,
    )

    assert result["status"] == "NO_TRADE"
    assert result["audit"]["latest"] == []
    assert result["audit"]["summary"]["total"] == 0
