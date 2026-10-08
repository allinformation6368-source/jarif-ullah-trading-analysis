from analysis.execution_audit import (
    create_execution_audit,
    persist_execution_audit,
    read_execution_audits,
)


def test_persist_execution_audit(tmp_path):
    audit_file = tmp_path / "execution_audit.jsonl"

    audit = create_execution_audit(
        {
            "status": "PAPER_ACCEPTED",
            "mode": "PAPER",
            "account_balance": 10000,
            "risk_percent": 1,
            "risk_reward": 2,
        },
        {
            "signal": "BUY",
            "entry": 100,
            "stop_loss": 95,
            "take_profit": 110,
        },
    )

    result = persist_execution_audit(
        audit,
        audit_file,
    )

    assert result["status"] == "SAVED"
    assert audit_file.exists()

    records = read_execution_audits(audit_file)

    assert len(records) == 1
    assert records[0]["execution_status"] == "PAPER_ACCEPTED"
    assert records[0]["signal"] == "BUY"


def test_multiple_audits_are_appended(tmp_path):
    audit_file = tmp_path / "execution_audit.jsonl"

    for signal in ("BUY", "SELL"):
        audit = create_execution_audit(
            {
                "status": "PAPER_ACCEPTED",
                "mode": "PAPER",
            },
            {
                "signal": signal,
                "entry": 100,
                "stop_loss": 95,
                "take_profit": 110,
            },
        )

        persist_execution_audit(
            audit,
            audit_file,
        )

    records = read_execution_audits(audit_file)

    assert len(records) == 2
    assert records[0]["signal"] == "BUY"
    assert records[1]["signal"] == "SELL"


def test_missing_audit_file_returns_empty_list(tmp_path):
    audit_file = tmp_path / "missing.jsonl"

    assert read_execution_audits(audit_file) == []


def test_invalid_json_record_is_skipped(tmp_path):
    audit_file = tmp_path / "execution_audit.jsonl"

    audit_file.write_text(
        '{"execution_status":"PAPER_ACCEPTED"}\n'
        '{invalid-json}\n'
        '{"signal":"SELL"}\n',
        encoding="utf-8",
    )

    records = read_execution_audits(audit_file)

    assert len(records) == 2
    assert records[0]["execution_status"] == "PAPER_ACCEPTED"
    assert records[1]["signal"] == "SELL"


def test_audit_log_rotates_when_size_limit_is_reached(tmp_path):
    audit_file = tmp_path / "execution_audit.jsonl"
    rotated_file = tmp_path / "execution_audit.jsonl.1"

    audit_file.write_text("x" * 100, encoding="utf-8")

    audit = create_execution_audit(
        {
            "status": "PAPER_ACCEPTED",
            "mode": "PAPER",
        },
        {
            "signal": "BUY",
            "entry": 100,
            "stop_loss": 95,
            "take_profit": 110,
        },
    )

    result = persist_execution_audit(
        audit,
        audit_file=audit_file,
        max_bytes=50,
        rotated_file=rotated_file,
    )

    assert result["status"] == "SAVED"
    assert rotated_file.exists()
    assert audit_file.exists()
    assert audit_file.stat().st_size > 0


def test_invalid_rotation_size_is_rejected(tmp_path):
    from analysis.execution_audit import rotate_execution_audit

    audit_file = tmp_path / "execution_audit.jsonl"
    audit_file.write_text("test", encoding="utf-8")

    result = rotate_execution_audit(
        audit_file=audit_file,
        max_bytes=0,
    )

    assert result["status"] == "REJECTED"


def test_query_execution_audits_by_status(tmp_path):
    audit_file = tmp_path / "execution_audit.jsonl"

    for status in ("PAPER_ACCEPTED", "REJECTED", "PAPER_ACCEPTED"):
        audit = create_execution_audit(
            {
                "status": status,
                "mode": "PAPER",
            },
            {
                "signal": "BUY",
                "entry": 100,
                "stop_loss": 95,
                "take_profit": 110,
            },
        )
        persist_execution_audit(audit, audit_file)

    from analysis.execution_audit import query_execution_audits

    records = query_execution_audits(
        audit_file,
        execution_status="PAPER_ACCEPTED",
    )

    assert len(records) == 2
    assert all(
        record["execution_status"] == "PAPER_ACCEPTED"
        for record in records
    )


def test_query_execution_audits_by_signal_and_mode(tmp_path):
    audit_file = tmp_path / "execution_audit.jsonl"

    entries = (
        ("BUY", "PAPER"),
        ("SELL", "PAPER"),
        ("BUY", "PAPER"),
    )

    for signal, mode in entries:
        audit = create_execution_audit(
            {
                "status": "PAPER_ACCEPTED",
                "mode": mode,
            },
            {
                "signal": signal,
                "entry": 100,
                "stop_loss": 95,
                "take_profit": 110,
            },
        )
        persist_execution_audit(audit, audit_file)

    from analysis.execution_audit import query_execution_audits

    records = query_execution_audits(
        audit_file,
        signal="BUY",
        mode="PAPER",
    )

    assert len(records) == 2
    assert all(record["signal"] == "BUY" for record in records)


def test_query_execution_audits_limit_returns_latest(tmp_path):
    audit_file = tmp_path / "execution_audit.jsonl"

    for signal in ("BUY", "SELL", "BUY"):
        audit = create_execution_audit(
            {
                "status": "PAPER_ACCEPTED",
                "mode": "PAPER",
            },
            {
                "signal": signal,
                "entry": 100,
                "stop_loss": 95,
                "take_profit": 110,
            },
        )
        persist_execution_audit(audit, audit_file)

    from analysis.execution_audit import query_execution_audits

    records = query_execution_audits(
        audit_file,
        limit=2,
    )

    assert len(records) == 2
    assert records[0]["signal"] == "SELL"
    assert records[1]["signal"] == "BUY"


def test_query_execution_audits_invalid_limit(tmp_path):
    audit_file = tmp_path / "execution_audit.jsonl"

    from analysis.execution_audit import query_execution_audits

    assert query_execution_audits(
        audit_file,
        limit=0,
    ) == []

    assert query_execution_audits(
        audit_file,
        limit="2",
    ) == []


def test_summarize_execution_audits(tmp_path):
    audit_file = tmp_path / "execution_audit.jsonl"

    entries = (
        ("PAPER_ACCEPTED", "BUY", "PAPER", None),
        ("PAPER_ACCEPTED", "SELL", "PAPER", None),
        ("REJECTED", "BUY", "PAPER", "Invalid order"),
        ("REJECTED", None, "LIVE", "Live execution adapter is not enabled"),
    )

    for status, signal, mode, reason in entries:
        result = {
            "status": status,
            "mode": mode,
        }

        if reason:
            result["reason"] = reason

        order = None
        if signal:
            order = {
                "signal": signal,
                "entry": 100,
                "stop_loss": 95,
                "take_profit": 110,
            }

        audit = create_execution_audit(result, order)
        persist_execution_audit(audit, audit_file)

    from analysis.execution_audit import summarize_execution_audits

    summary = summarize_execution_audits(audit_file)

    assert summary["total"] == 4
    assert summary["accepted"] == 2
    assert summary["rejected"] == 2
    assert summary["buy"] == 2
    assert summary["sell"] == 1
    assert summary["paper"] == 3
    assert summary["live"] == 1
    assert summary["rejection_reasons"]["Invalid order"] == 1
    assert (
        summary["rejection_reasons"]
        ["Live execution adapter is not enabled"]
        == 1
    )


def test_summarize_empty_audit_file(tmp_path):
    audit_file = tmp_path / "missing.jsonl"

    from analysis.execution_audit import summarize_execution_audits

    summary = summarize_execution_audits(audit_file)

    assert summary["total"] == 0
    assert summary["accepted"] == 0
    assert summary["rejected"] == 0
    assert summary["buy"] == 0
    assert summary["sell"] == 0
    assert summary["paper"] == 0
    assert summary["live"] == 0
    assert summary["rejection_reasons"] == {}
