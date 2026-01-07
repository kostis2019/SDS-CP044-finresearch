# tests/test_factor_scoring_tools.py

from tools.factor_scoring_tools import compute_factor_scores


def test_compute_factor_scores_basic():
    fundamentals = {
        "growth": {
            "revenue_cagr_3y": 0.15,
            "eps_cagr_3y": 0.18,
            "revenue_yoy": 0.20,
        },
        "profitability": {
            "roe": 0.22,
            "operating_margin": 0.28,
        },
        "financial_health": {
            "debt_equity": 0.4,
            "interest_coverage": 8,
        },
    }

    technicals = {
        "rsi14": 55,
        "trend_label": "uptrend",
        "max_drawdown_1y": -0.18,
    }

    scores = compute_factor_scores(fundamentals, technicals)

    assert scores["growth_score"] > 60
    assert scores["technical_score"] > 60
    assert scores["final_score"] > 50
    assert scores["rating"] in ["Buy", "Hold", "Strong Buy"]
