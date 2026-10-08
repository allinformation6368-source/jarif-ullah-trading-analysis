from analysis.mtf_engine import analyze_multi_timeframe
from analysis.paper_trading import run_paper_session


def test_real_mtf_engine_paper_session_compatibility():
    candles = []

    base = 100.0

    for i in range(40):
        close = base + (i * 0.5)

        candles.append({
            "datetime": f"2026-01-01T00:{i:02d}:00+00:00",
            "open": close - 0.2,
            "high": close + 0.8,
            "low": close - 0.8,
            "close": close,
        })

    result = run_paper_session(
        candles=candles,
        analyze_function=lambda history, account_balance=10000, risk_percent=1: (
            analyze_multi_timeframe(
                {"15m": history},
                account_balance=account_balance,
                risk_percent=risk_percent,
            )
        ),
        account_balance=10000,
        risk_percent=1,
    )

    assert result["status"] == "VALID"
    assert isinstance(result["orders"], list)
    assert result["account"]["status"] == "READY"
    assert result["account"]["starting_balance"] == 10000
    assert result["account"]["balance"] >= 0


def test_real_mtf_engine_direct_output_contains_paper_order():
    candles = []

    for i in range(40):
        close = 100.0 + (i * 0.5)

        candles.append({
            "datetime": f"2026-01-01T00:{i:02d}:00+00:00",
            "open": close - 0.2,
            "high": close + 0.8,
            "low": close - 0.8,
            "close": close,
        })

    result = analyze_multi_timeframe(
        {"15m": candles},
        account_balance=10000,
        risk_percent=1,
    )

    assert "trade_plan" in result
    assert "paper_order" in result

    if result["trade_plan"].get("status") == "READY":
        assert result["paper_order"] is not None
        assert result["paper_order"]["status"] == "OPEN"
    else:
        assert result["paper_order"] is None
