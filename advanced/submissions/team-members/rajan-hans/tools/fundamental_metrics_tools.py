# tools/fundamentals_metrics_tools.py
# Compute key fundamental metrics from financial statements
# ---------------------------------------------


import math


class FundamentalMetricsError(Exception):
    """Raised when fundamental metrics cannot be computed."""


def _safe_div(numerator, denominator):
    if numerator is None or denominator in (None, 0):
        return None
    return numerator / denominator


def _cagr(start, end, years):
    if start in (None, 0) or end in (None, 0) or years <= 0:
        return None
    try:
        return (end / start) ** (1 / years) - 1
    except Exception:
        return None


def compute_fundamental_metrics(fundamentals: dict) -> dict:
    """
    Compute growth, profitability, and financial health metrics.

    Parameters
    ----------
    fundamentals : dict
        Expected keys:
        - income_statement: list[dict]
        - balance_sheet: list[dict]
        - cash_flow: list[dict]

    Returns
    -------
    dict
        {
          "growth": {...},
          "profitability": {...},
          "financial_health": {...}
        }
    """

    income = fundamentals.get("income_statement", [])
    balance = fundamentals.get("balance_sheet", [])
    cashflow = fundamentals.get("cash_flow", [])

    if len(income) < 2 or len(balance) < 1:
        raise FundamentalMetricsError("Insufficient fundamental data.")

    # Assume most recent first
    latest_inc = income[0]
    prev_inc = income[1]

    latest_bal = balance[0]

    # -----------------------------
    # GROWTH METRICS
    # -----------------------------
    revenues = [row.get("revenue") for row in income if row.get("revenue") is not None]
    eps_values = [row.get("eps") for row in income if row.get("eps") is not None]

    revenue_cagr = None
    eps_cagr = None

    if len(revenues) >= 4:
        revenue_cagr = _cagr(revenues[-1], revenues[0], 3)

    if len(eps_values) >= 4:
        eps_cagr = _cagr(eps_values[-1], eps_values[0], 3)

    revenue_yoy = _safe_div(
        latest_inc.get("revenue") - prev_inc.get("revenue"),
        prev_inc.get("revenue"),
    )

    eps_yoy = _safe_div(
        latest_inc.get("eps") - prev_inc.get("eps"),
        abs(prev_inc.get("eps")) if prev_inc.get("eps") else None,
    )

    # Growth trend label
    growth_trend = "unknown"
    if revenue_yoy is not None:
        if revenue_yoy > 0.10:
            growth_trend = "accelerating"
        elif revenue_yoy > 0.03:
            growth_trend = "stable"
        else:
            growth_trend = "slowing"

    growth = {
        "revenue_cagr_3y": revenue_cagr,
        "eps_cagr_3y": eps_cagr,
        "revenue_yoy": revenue_yoy,
        "eps_yoy": eps_yoy,
        "growth_trend": growth_trend,
    }

    # -----------------------------
    # PROFITABILITY METRICS
    # -----------------------------
    revenue = latest_inc.get("revenue")
    gross_profit = latest_inc.get("gross_profit")
    operating_income = latest_inc.get("operating_income")
    net_income = latest_inc.get("net_income")

    gross_margin = _safe_div(gross_profit, revenue)
    operating_margin = _safe_div(operating_income, revenue)
    net_margin = _safe_div(net_income, revenue)

    equity = latest_bal.get("total_equity")
    assets = latest_bal.get("total_assets")

    roe = _safe_div(net_income, equity)
    roa = _safe_div(net_income, assets)

    profitability_level = "unknown"
    if roe is not None:
        if roe >= 0.20:
            profitability_level = "high"
        elif roe >= 0.10:
            profitability_level = "medium"
        else:
            profitability_level = "low"

    profitability = {
        "gross_margin": gross_margin,
        "operating_margin": operating_margin,
        "net_margin": net_margin,
        "roe": roe,
        "roa": roa,
        "profitability_level": profitability_level,
    }

    # -----------------------------
    # FINANCIAL HEALTH METRICS
    # -----------------------------
    total_debt = latest_bal.get("total_debt")
    cash = latest_bal.get("cash_and_equivalents")
    current_assets = latest_bal.get("current_assets")
    current_liabilities = latest_bal.get("current_liabilities")

    interest_expense = latest_inc.get("interest_expense")
    ebit = latest_inc.get("ebit")

    debt_equity = _safe_div(total_debt, equity)
    cash_to_debt = _safe_div(cash, total_debt)
    current_ratio = _safe_div(current_assets, current_liabilities)
    interest_coverage = (
        _safe_div(ebit, abs(interest_expense)) if interest_expense else None
    )

    balance_strength = "unknown"
    if debt_equity is not None:
        if debt_equity <= 0.5:
            balance_strength = "strong"
        elif debt_equity <= 1.0:
            balance_strength = "acceptable"
        else:
            balance_strength = "weak"

    financial_health = {
        "debt_equity": debt_equity,
        "interest_coverage": interest_coverage,
        "cash_to_debt": cash_to_debt,
        "current_ratio": current_ratio,
        "balance_sheet_strength": balance_strength,
    }

    return {
        "growth": growth,
        "profitability": profitability,
        "financial_health": financial_health,
    }
