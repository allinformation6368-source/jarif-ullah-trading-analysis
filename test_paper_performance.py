from analysis.paper_performance import (
    calculate_max_drawdown,
    calculate_paper_performance,
)


def test_empty_trades_returns_zero_metrics():
    result = calculate_paper_performance([], starting_equity=10000)

    assert result["status"] == "VALID"
    assert result["total_trades"] == 0
    assert result["net_pnl"] == 0.0
    assert result["win_rate"] == 0.0
    assert result["ending_equity"] == 10000.0


def test_paper_performance_calculates_core_metrics():
    trades = [
        {"pnl": 100.0, "risk_amount": 50.0},
        {"pnl": -40.0, "risk_amount": 50.0},
        {"pnl": 60.0, "risk_amount": 30.0},
    ]

    result = calculate_paper_performance(
        trades,
        starting_equity=10000,
    )

    assert result["status"] == "VALID"
    assert result["total_trades"] == 3
    assert result["winning_trades"] == 2
    assert result["losing_trades"] == 1
    assert result["win_rate"] == 2 / 3 * 100
    assert result["gross_profit"] == 160.0
    assert result["gross_loss"] == 40.0
    assert result["net_pnl"] == 120.0
    assert result["average_pnl"] == 40.0
    assert result["profit_factor"] == 4.0
    assert result["ending_equity"] == 10120.0
    assert result["average_r"] == (2.0 - 0.8 + 2.0) / 3


def test_max_drawdown_is_calculated_from_equity_curve():
    pnls = [100.0, -50.0, -100.0, 200.0]

    assert calculate_max_drawdown(
        pnls,
        starting_equity=1000,
    ) == 150.0


def test_all_winning_trades_have_infinite_profit_factor():
    result = calculate_paper_performance(
        [{"pnl": 100.0}, {"pnl": 50.0}],
    )

    assert result["status"] == "VALID"
    assert result["profit_factor"] == float("inf")
    assert result["losing_trades"] == 0


def test_all_zero_pnl_has_zero_profit_factor():
    result = calculate_paper_performance(
        [{"pnl": 0.0}, {"pnl": 0.0}],
    )

    assert result["status"] == "VALID"
    assert result["profit_factor"] == 0.0
    assert result["win_rate"] == 0.0


def test_invalid_trades_are_rejected():
    result = calculate_paper_performance("invalid")

    assert result["status"] == "REJECTED"


def test_missing_pnl_is_rejected():
    result = calculate_paper_performance(
        [{"signal": "BUY"}],
    )

    assert result["status"] == "REJECTED"
    assert result["reason"] == "Trade is missing pnl"


def test_invalid_starting_equity_is_rejected():
    result = calculate_paper_performance(
        [{"pnl": 10.0}],
        starting_equity="10000",
    )

    assert result["status"] == "REJECTED"
