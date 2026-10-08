from analysis.risk_management import calculate_smc_risk_from_candles


def test_long_entry_from_latest_close():
    candles = [
        {
            "datetime": "2026-10-07T10:00:00",
            "open": 98,
            "high": 101,
            "low": 97,
            "close": 100,
        },
        {
            "datetime": "2026-10-07T10:05:00",
            "open": 100,
            "high": 103,
            "low": 99,
            "close": 102,
        },
    ]

    analysis = {
        "structure": {
            "lows": [
                {"type": "LOW", "price": 98},
            ],
            "highs": [],
        },
        "order_blocks": [],
    }

    result = calculate_smc_risk_from_candles(
        signal="LONG",
        candles=candles,
        analysis=analysis,
        risk_reward=2,
    )

    assert result["status"] == "VALID"
    assert result["entry"] == 102
    assert result["stop_loss"] == 98
    assert result["take_profit"] == 110
    assert result["risk"] == 4
    assert result["reward"] == 8
    assert result["risk_reward"] == 2
    assert result["sl_source"] == "STRUCTURE"


def test_short_entry_from_latest_close():
    candles = [
        {
            "datetime": "2026-10-07T10:00:00",
            "open": 102,
            "high": 104,
            "low": 100,
            "close": 102,
        },
        {
            "datetime": "2026-10-07T10:05:00",
            "open": 102,
            "high": 103,
            "low": 97,
            "close": 98,
        },
    ]

    analysis = {
        "structure": {
            "lows": [],
            "highs": [
                {"type": "HIGH", "price": 103},
            ],
        },
        "order_blocks": [],
    }

    result = calculate_smc_risk_from_candles(
        signal="SHORT",
        candles=candles,
        analysis=analysis,
        risk_reward=2,
    )

    assert result["status"] == "VALID"
    assert result["entry"] == 98
    assert result["stop_loss"] == 103
    assert result["take_profit"] == 88
    assert result["risk"] == 5
    assert result["reward"] == 10
    assert result["risk_reward"] == 2
    assert result["sl_source"] == "STRUCTURE"


def test_empty_candles():
    analysis = {
        "structure": {
            "lows": [],
            "highs": [],
        },
        "order_blocks": [],
    }

    result = calculate_smc_risk_from_candles(
        signal="LONG",
        candles=[],
        analysis=analysis,
        risk_reward=2,
    )

    assert result["status"] == "REJECTED"


if __name__ == "__main__":
    test_long_entry_from_latest_close()
    test_short_entry_from_latest_close()
    test_empty_candles()

    print("SMC RISK ENTRY CONTRACT TEST: SUCCESS")
