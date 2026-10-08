from analysis.risk_management import calculate_smc_risk_from_analysis


def test_long_structure_anchor():
    analysis = {
        "structure": {
            "lows": [
                {"type": "LOW", "price": 95},
                {"type": "LOW", "price": 98},
            ]
        },
        "order_blocks": [
            {
                "type": "BULLISH_OB",
                "low": 94,
                "high": 100,
            }
        ],
    }

    result = calculate_smc_risk_from_analysis(
        signal="LONG",
        entry=100,
        analysis=analysis,
        risk_reward=2,
    )

    assert result["status"] == "VALID"
    assert result["stop_loss"] == 98
    assert result["take_profit"] == 104
    assert result["risk_reward"] == 2
    assert result["sl_source"] == "STRUCTURE"


def test_short_structure_anchor():
    analysis = {
        "structure": {
            "highs": [
                {"type": "HIGH", "price": 105},
                {"type": "HIGH", "price": 103},
            ]
        },
        "order_blocks": [
            {
                "type": "BEARISH_OB",
                "low": 100,
                "high": 106,
            }
        ],
    }

    result = calculate_smc_risk_from_analysis(
        signal="SHORT",
        entry=100,
        analysis=analysis,
        risk_reward=2,
    )

    assert result["status"] == "VALID"
    assert result["stop_loss"] == 103
    assert result["take_profit"] == 94
    assert result["risk_reward"] == 2
    assert result["sl_source"] == "STRUCTURE"


def test_long_order_block_fallback():
    analysis = {
        "structure": {
            "lows": []
        },
        "order_blocks": [
            {
                "type": "BULLISH_OB",
                "low": 95,
                "high": 101,
            }
        ],
    }

    result = calculate_smc_risk_from_analysis(
        signal="LONG",
        entry=100,
        analysis=analysis,
        risk_reward=2,
    )

    assert result["status"] == "VALID"
    assert result["stop_loss"] == 95
    assert result["take_profit"] == 110
    assert result["sl_source"] == "ORDER_BLOCK"


def test_short_order_block_fallback():
    analysis = {
        "structure": {
            "highs": []
        },
        "order_blocks": [
            {
                "type": "BEARISH_OB",
                "low": 99,
                "high": 105,
            }
        ],
    }

    result = calculate_smc_risk_from_analysis(
        signal="SHORT",
        entry=100,
        analysis=analysis,
        risk_reward=2,
    )

    assert result["status"] == "VALID"
    assert result["stop_loss"] == 105
    assert result["take_profit"] == 90
    assert result["sl_source"] == "ORDER_BLOCK"


def test_no_valid_anchor():
    analysis = {
        "structure": {
            "lows": [],
            "highs": [],
        },
        "order_blocks": [],
    }

    result = calculate_smc_risk_from_analysis(
        signal="LONG",
        entry=100,
        analysis=analysis,
        risk_reward=2,
    )

    assert result["status"] == "REJECTED"


if __name__ == "__main__":
    test_long_structure_anchor()
    test_short_structure_anchor()
    test_long_order_block_fallback()
    test_short_order_block_fallback()
    test_no_valid_anchor()

    print("SMC RISK ANCHOR CONTRACT TEST: SUCCESS")
