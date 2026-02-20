# tests/test_fundamentals_tools.py

from tools.fundamentals_tools import get_fundamentals


def test_get_fundamentals_basic():
    data = get_fundamentals("AAPL")

    assert "income_statement" in data
    assert "balance_sheet" in data
    assert "cash_flow" in data

    assert len(data["income_statement"]) >= 2
    assert isinstance(data["income_statement"][0], dict)


def test_income_statement_has_revenue():
    data = get_fundamentals("AAPL")
    assert "revenue" in data["income_statement"][0]
