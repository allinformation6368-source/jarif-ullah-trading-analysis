from analysis.paper_trading import (
    create_paper_order,
    update_paper_order,
    calculate_paper_balance,
    process_paper_position,
    calculate_open_positions,
)


def ready_plan(signal="BUY"):
    return {
        "status": "READY",
        "signal": signal,
        "entry": 100,
        "stop_loss": 95 if signal == "BUY" else 105,
        "take_profit": 110 if signal == "BUY" else 90,
    }


def test_create_buy_paper_order():
    order = create_paper_order(
        ready_plan("BUY"),
        account_balance=10000,
    )

    assert order["status"] == "OPEN"
    assert order["signal"] == "BUY"
    assert order["entry"] == 100
    assert order["stop_loss"] == 95
    assert order["take_profit"] == 110


def test_create_sell_paper_order():
    order = create_paper_order(
        ready_plan("SELL"),
        account_balance=10000,
    )

    assert order["status"] == "OPEN"
    assert order["signal"] == "SELL"


def test_reject_invalid_trade_plan():
    result = create_paper_order(
        {"status": "WAIT"},
    )

    assert result["status"] == "REJECTED"


def test_buy_take_profit_closes_win():
    order = create_paper_order(ready_plan("BUY"))

    result = update_paper_order(
        order,
        {"high": 111, "low": 99},
    )

    assert result["status"] == "CLOSED"
    assert result["result"] == "WIN"
    assert result["exit_price"] == 110
    assert result["pnl"] == 10


def test_buy_stop_loss_closes_loss():
    order = create_paper_order(ready_plan("BUY"))

    result = update_paper_order(
        order,
        {"high": 101, "low": 94},
    )

    assert result["status"] == "CLOSED"
    assert result["result"] == "LOSS"
    assert result["exit_price"] == 95
    assert result["pnl"] == -5


def test_sell_take_profit_closes_win():
    order = create_paper_order(ready_plan("SELL"))

    result = update_paper_order(
        order,
        {"high": 101, "low": 89},
    )

    assert result["status"] == "CLOSED"
    assert result["result"] == "WIN"
    assert result["exit_price"] == 90
    assert result["pnl"] == 10


def test_sell_stop_loss_closes_loss():
    order = create_paper_order(ready_plan("SELL"))

    result = update_paper_order(
        order,
        {"high": 106, "low": 99},
    )

    assert result["status"] == "CLOSED"
    assert result["result"] == "LOSS"
    assert result["exit_price"] == 105
    assert result["pnl"] == -5


def test_open_order_remains_open():
    order = create_paper_order(ready_plan("BUY"))

    result = update_paper_order(
        order,
        {"high": 105, "low": 98},
    )

    assert result["status"] == "OPEN"
    assert result["result"] is None
    assert result["pnl"] == 0


def test_paper_balance():
    orders = [
        {"status": "CLOSED", "result": "WIN", "pnl": 10},
        {"status": "CLOSED", "result": "LOSS", "pnl": -5},
        {"status": "OPEN", "pnl": 0},
    ]

    result = calculate_paper_balance(
        starting_balance=10000,
        orders=orders,
    )

    assert result["starting_balance"] == 10000
    assert result["total_pnl"] == 5
    assert result["ending_balance"] == 10005
    assert result["closed_trades"] == 2


def test_process_paper_position_closes_on_later_candle():
    order = create_paper_order(ready_plan("BUY"))

    result = process_paper_position(
        order,
        [
            {"high": 104, "low": 98},
            {"high": 111, "low": 101},
        ],
    )

    assert result["status"] == "CLOSED"
    assert result["result"] == "WIN"
    assert result["exit_price"] == 110
    assert result["pnl"] == 10


def test_process_paper_position_stops_on_stop_loss():
    order = create_paper_order(ready_plan("SELL"))

    result = process_paper_position(
        order,
        [
            {"high": 103, "low": 97},
            {"high": 106, "low": 99},
        ],
    )

    assert result["status"] == "CLOSED"
    assert result["result"] == "LOSS"
    assert result["exit_price"] == 105
    assert result["pnl"] == -5


def test_process_paper_position_remains_open():
    order = create_paper_order(ready_plan("BUY"))

    result = process_paper_position(
        order,
        [
            {"high": 103, "low": 98},
            {"high": 107, "low": 99},
        ],
    )

    assert result["status"] == "OPEN"
    assert result["result"] is None
    assert result["pnl"] == 0


def test_calculate_open_positions():
    orders = [
        {"status": "OPEN", "signal": "BUY"},
        {"status": "CLOSED", "signal": "SELL"},
        {"status": "OPEN", "signal": "SELL"},
    ]

    result = calculate_open_positions(orders)

    assert result["status"] == "VALID"
    assert result["open_positions"] == 2
    assert len(result["orders"]) == 2
