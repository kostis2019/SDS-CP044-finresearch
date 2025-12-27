# tests/test_fundamental_metrics.py

from tools.fundamental_metrics_tools import compute_fundamental_metrics


def test_compute_fundamental_metrics_basic():
    fundamentals = {
        "income_statement": [
            {
                "revenue": 100,
                "gross_profit": 60,
                "operating_income": 30,
                "net_income": 25,
                "eps": 5,
                "interest_expense": 2,
                "ebit": 32,
            },
            {
                "revenue": 90,
                "gross_profit": 55,
                "operating_income": 28,
                "net_income": 22,
                "eps": 4.5,
            },
            {
                "revenue": 80,
                "eps": 4,
            },
            {
                "revenue": 70,
                "eps": 3.5,
            },
        ],
        "balance_sheet": [
            {
                "total_debt": 20,
                "total_equity": 100,
                "total_assets": 150,
                "cash_and_equivalents": 30,
                "current_assets": 80,
                "current_liabilities": 40,
            }
        ],
        "cash_flow": [],
    }

    result = compute_fundamental_metrics(fundamentals)

    assert "growth" in result
    assert "profitability" in result
    assert "financial_health" in result

    assert result["profitability"]["gross_margin"] == 0.6
    assert result["financial_health"]["debt_equity"] == 0.2
    assert result["growth"]["growth_trend"] in ["accelerating", "stable", "slowing"]
