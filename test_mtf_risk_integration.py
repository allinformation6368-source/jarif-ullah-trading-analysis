from analysis.mtf_engine import analyze_multi_timeframe


def make_bullish_candles():
    return [
        {"datetime": "2026-10-07T09:15:00", "open": 100, "high": 103, "low": 99, "close": 101},
        {"datetime": "2026-10-07T09:20:00", "open": 101, "high": 105, "low": 99, "close": 103},
        {"datetime": "2026-10-07T09:25:00", "open": 103, "high": 106, "low": 97, "close": 102},
        {"datetime": "2026-10-07T09:30:00", "open": 102, "high": 104, "low": 99, "close": 100},
        {"datetime": "2026-10-07T09:35:00", "open": 100, "high": 105, "low": 97, "close": 103},
        {"datetime": "2026-10-07T09:40:00", "open": 103, "high": 108, "low": 101, "close": 106},
        {"datetime": "2026-10-07T09:45:00", "open": 106, "high": 107, "low": 99, "close": 102},
        {"datetime": "2026-10-07T09:50:00", "open": 102, "high": 110, "low": 95, "close": 109},
        {"datetime": "2026-10-07T09:55:00", "open": 109, "high": 110, "low": 103, "close": 105},
        {"datetime": "2026-10-07T10:00:00", "open": 105, "high": 107, "low": 104, "close": 106},
        {"datetime": "2026-10-07T10:05:00", "open": 106, "high": 114, "low": 108, "close": 113},
        {"datetime": "2026-10-07T10:10:00", "open": 113, "high": 116, "low": 110, "close": 115},
        {"datetime": "2026-10-07T10:15:00", "open": 115, "high": 116, "low": 106, "close": 109},
        {"datetime": "2026-10-07T10:20:00", "open": 109, "high": 112, "low": 98, "close": 100},
    ]


def test_mtf_ready_calculates_real_risk():
    candles = make_bullish_candles()

    result = analyze_multi_timeframe(
        {
            "5m": candles,
            "15m": candles,
            "1h": candles,
        }
    )

    assert result["decision"]["decision"] == "ENTRY_READY"
    assert result["decision"]["signal"] == "LONG"

    risk = result["risk"]

    assert risk is not None
    assert risk["status"] == "VALID"
    assert risk["entry"] == 100
    assert risk["stop_loss"] < risk["entry"]
    assert risk["take_profit"] > risk["entry"]
    assert risk["risk"] > 0
    assert risk["reward"] > risk["risk"]
    assert risk["risk_reward"] == 2
    assert risk["sl_source"] in ("STRUCTURE", "ORDER_BLOCK")


def test_mtf_wait_has_no_risk():
    result = analyze_multi_timeframe(
        {
            "5m": [],
            "15m": [],
            "1h": [],
        }
    )

    assert result["decision"]["decision"] == "WAIT"
    assert result["risk"] is None


def test_mtf_ready_calculates_position_size():
    candles = make_bullish_candles()

    result = analyze_multi_timeframe(
        {
            "5m": candles,
            "15m": candles,
            "1h": candles,
        },
        account_balance=10000,
        risk_percent=1,
    )

    assert result["decision"]["decision"] == "ENTRY_READY"

    risk = result["risk"]

    assert risk is not None
    assert risk["status"] == "VALID"

    sizing = result["position_sizing"]

    assert sizing is not None
    assert sizing["status"] == "VALID"
    assert sizing["account_balance"] == 10000
    assert sizing["risk_percent"] == 1
    assert sizing["risk_amount"] == 100
    assert sizing["entry"] == risk["entry"]
    assert sizing["stop_loss"] == risk["stop_loss"]
    assert sizing["position_size"] > 0


if __name__ == "__main__":
    test_mtf_ready_calculates_real_risk()
    test_mtf_wait_has_no_risk()
    test_mtf_ready_calculates_position_size()

    print("MTF RISK + POSITION SIZING CONTRACT TEST: SUCCESS")


def test_mtf_ready_risk_guard_is_approved():
    candles = make_bullish_candles()

    result = analyze_multi_timeframe(
        {
            "5m": candles,
            "15m": candles,
            "1h": candles,
        },
        account_balance=10000,
        risk_percent=1,
    )

    guard = result["risk_guard"]

    assert guard is not None
    assert guard["status"] == "APPROVED"
    assert guard["signal"] == "LONG"
    assert guard["entry"] == result["risk"]["entry"]
    assert guard["stop_loss"] == result["risk"]["stop_loss"]


def test_mtf_wait_has_no_risk_guard():
    result = analyze_multi_timeframe(
        {
            "5m": [],
            "15m": [],
            "1h": [],
        }
    )

    assert result["risk"] is None
    assert result["position_sizing"] is None
    assert result["risk_guard"] is None


if __name__ == "__main__":
    test_mtf_ready_calculates_real_risk()
    test_mtf_wait_has_no_risk()
    test_mtf_ready_calculates_position_size()
    test_mtf_ready_risk_guard_is_approved()
    test_mtf_wait_has_no_risk_guard()

    print("MTF RISK + POSITION SIZING + RISK GUARD CONTRACT TEST: SUCCESS")


def test_mtf_ready_has_unified_trade_plan():
    candles = make_bullish_candles()

    result = analyze_multi_timeframe(
        {
            "5m": candles,
            "15m": candles,
            "1h": candles,
        },
        account_balance=10000,
        risk_percent=1,
    )

    plan = result["trade_plan"]

    assert plan is not None
    assert plan["status"] == "READY"
    assert plan["signal"] == "LONG"
    assert plan["entry"] == result["risk"]["entry"]
    assert plan["stop_loss"] == result["risk"]["stop_loss"]
    assert plan["take_profit"] == result["risk"]["take_profit"]
    assert plan["position_size"] == result["position_sizing"]["position_size"]
    assert plan["risk_guard"] == "APPROVED"


def test_mtf_wait_has_no_unified_trade_plan():
    result = analyze_multi_timeframe(
        {
            "5m": [],
            "15m": [],
            "1h": [],
        }
    )

    assert result["decision"]["decision"] == "WAIT"
    assert result["trade_plan"]["status"] == "WAIT"


def test_mtf_has_market_regime():
    candles = make_bullish_candles()

    result = analyze_multi_timeframe(
        {
            "5m": candles,
            "15m": candles,
            "1h": candles,
        },
        account_balance=10000,
        risk_percent=1,
    )

    regime = result["market_regime"]

    assert regime is not None
    assert regime["status"] == "VALID"
    assert regime["regime"] in (
        "TRENDING_BULLISH",
        "TRENDING_BEARISH",
        "RANGING",
        "NEUTRAL",
    )


def test_mtf_empty_data_has_no_market_regime():
    result = analyze_multi_timeframe(
        {
            "5m": [],
            "15m": [],
            "1h": [],
        }
    )

    assert result["market_regime"] is None


def test_mtf_has_session_filter():
    candles = make_bullish_candles()

    result = analyze_multi_timeframe(
        {
            "5m": candles,
            "15m": candles,
            "1h": candles,
        },
        account_balance=10000,
        risk_percent=1,
    )

    session = result["session"]
    session_filter = result["session_filter"]

    assert session is not None
    assert session["status"] == "VALID"
    assert session["session"] in (
        "ASIA",
        "LONDON",
        "NEW_YORK",
        "OFF_SESSION",
    )

    assert session_filter is not None
    assert session_filter["status"] in (
        "APPROVED",
        "BLOCKED",
    )


def test_mtf_empty_data_has_no_session():
    result = analyze_multi_timeframe(
        {
            "5m": [],
            "15m": [],
            "1h": [],
        }
    )

    assert result["session"] is None
    assert result["session_filter"] is None


def test_mtf_blocked_session_prevents_entry():
    candles = make_bullish_candles()

    blocked_candles = []
    for candle in candles:
        updated = dict(candle)
        updated["datetime"] = "2026-10-07T22:30:00+00:00"
        blocked_candles.append(updated)

    result = analyze_multi_timeframe(
        {
            "5m": blocked_candles,
            "15m": blocked_candles,
            "1h": blocked_candles,
        },
        account_balance=10000,
        risk_percent=1,
    )

    assert result["session_filter"]["status"] == "BLOCKED"
    assert result["decision"]["decision"] == "WAIT"
    assert result["decision"]["reason"] == "Session not allowed"
    assert result["risk"] is None
    assert result["trade_plan"]["status"] == "WAIT"


def test_mtf_allowed_session_keeps_normal_flow():
    candles = make_bullish_candles()

    allowed_candles = []
    for candle in candles:
        updated = dict(candle)
        updated["datetime"] = "2026-10-07T10:30:00+00:00"
        allowed_candles.append(updated)

    result = analyze_multi_timeframe(
        {
            "5m": allowed_candles,
            "15m": allowed_candles,
            "1h": allowed_candles,
        },
        account_balance=10000,
        risk_percent=1,
    )

    assert result["session_filter"]["status"] == "APPROVED"
