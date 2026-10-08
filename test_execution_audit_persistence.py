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
