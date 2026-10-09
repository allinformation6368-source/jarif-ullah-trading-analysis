import json

from api.server import (
    BrainAPIHandler,
    build_analysis_response,
    _validate_request,
)


def test_validate_request_defaults():
    assert (
        _validate_request(
            {
                "symbol": "BTC/USD",
                "mode": "intraday",
            }
        )
        is None
    )


def test_validate_request_rejects_invalid_mode():
    assert (
        _validate_request(
            {
                "symbol": "BTC/USD",
                "mode": "invalid",
            }
        )
        == "Invalid mode"
    )


def test_validate_request_rejects_invalid_symbol():
    assert (
        _validate_request(
            {
                "symbol": "",
                "mode": "intraday",
            }
        )
        == "Invalid symbol"
    )


def test_validate_request_rejects_invalid_balance():
    assert (
        _validate_request(
            {
                "symbol": "BTC/USD",
                "mode": "intraday",
                "account_balance": 0,
            }
        )
        == "Invalid account balance"
    )


def test_validate_request_rejects_risk_above_limit():
    assert (
        _validate_request(
            {
                "symbol": "BTC/USD",
                "mode": "intraday",
                "risk_percent": 6,
            }
        )
        == "Risk percent outside allowed range"
    )


def test_build_analysis_response_matches_contract_shape():
    result = build_analysis_response(
        symbol="BTC/USD",
        mode="intraday",
        analysis={
            "decision": {
                "decision": "WAIT",
                "signal": "LONG",
                "confidence": 60,
            },
            "market_regime": {
                "regime": "NEUTRAL",
            },
            "session": {
                "session": "LONDON",
            },
            "trade_plan": {
                "status": "WAIT",
            },
            "risk": None,
            "position_sizing": None,
            "risk_guard": None,
            "paper_order": None,
        },
    )

    assert result["status"] == "VALID"
    assert result["symbol"] == "BTC/USD"
    assert result["mode"] == "intraday"

    analysis = result["analysis"]

    assert set(analysis) == {
        "decision",
        "market_regime",
        "session",
        "trade_plan",
        "risk",
        "position_sizing",
        "risk_guard",
        "paper_order",
    }


def test_api_handler_exists():
    assert issubclass(
        BrainAPIHandler,
        object,
    )
