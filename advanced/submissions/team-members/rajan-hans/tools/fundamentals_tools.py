# tools/fundamentals_tools.py

from datetime import date

# import yfinance as yf
from tools.yfinance_provider import get_yfinance_provider


class FundamentalsDataError(Exception):
    """Raised when fundamental data cannot be fetched or normalized."""


def _safe_get(record: dict, *keys):
    """Try multiple possible keys and return the first found."""
    for key in keys:
        if key in record and record[key] is not None:
            return record[key]
    return None


def _normalize_statement(df):
    """
    Convert yfinance DataFrame (columns = periods) into
    list of dicts (most recent first).
    """
    if df is None or df.empty:
        return []

    df = df.fillna(0)
    records = []

    for col in df.columns:
        row = df[col].to_dict()
        records.append(row)

    return records


def get_fundamentals(ticker: str) -> dict:
    """
    Fetch and normalize raw financial statements using yfinance.

    Parameters
    ----------
    ticker : str
        Stock ticker symbol (e.g., 'AAPL').

    Returns
    -------
    dict
        Raw normalized fundamentals:
        - income_statement
        - balance_sheet
        - cash_flow
    """

    if not ticker or not isinstance(ticker, str):
        raise FundamentalsDataError("Ticker must be a non-empty string.")

    try:
        provider = get_yfinance_provider()
        income_stmt = provider.get_financials(ticker)
        balance_sheet = provider.get_balance_sheet(ticker)
        cash_flow = provider.get_cashflow(ticker)

    except Exception as e:
        raise FundamentalsDataError(f"Failed to fetch fundamentals for {ticker}: {e}")

    if income_stmt is None or income_stmt.empty:
        raise FundamentalsDataError(f"No income statement data available for {ticker}.")

    # Normalize statements
    income_records = _normalize_statement(income_stmt)
    balance_records = _normalize_statement(balance_sheet)
    cashflow_records = _normalize_statement(cash_flow)

    # -----------------------------
    # Normalize income statement keys
    # -----------------------------
    normalized_income = []
    for rec in income_records:
        normalized_income.append(
            {
                "revenue": _safe_get(rec, "Total Revenue", "Revenue"),
                "gross_profit": _safe_get(rec, "Gross Profit"),
                "operating_income": _safe_get(
                    rec, "Operating Income", "Operating Income or Loss"
                ),
                "net_income": _safe_get(
                    rec, "Net Income", "Net Income Common Stockholders"
                ),
                "eps": _safe_get(rec, "Diluted EPS", "Basic EPS"),
                "interest_expense": _safe_get(rec, "Interest Expense"),
                "ebit": _safe_get(rec, "EBIT"),
            }
        )

    # -----------------------------
    # Normalize balance sheet keys
    # -----------------------------
    normalized_balance = []
    for rec in balance_records:
        normalized_balance.append(
            {
                "total_assets": _safe_get(rec, "Total Assets"),
                "total_equity": _safe_get(
                    rec, "Total Stockholder Equity", "Stockholders Equity"
                ),
                "total_debt": _safe_get(rec, "Total Debt"),
                "cash_and_equivalents": _safe_get(
                    rec, "Cash And Cash Equivalents", "Cash"
                ),
                "current_assets": _safe_get(rec, "Total Current Assets"),
                "current_liabilities": _safe_get(rec, "Total Current Liabilities"),
            }
        )

    # -----------------------------
    # Normalize cash flow keys
    # -----------------------------
    normalized_cashflow = []
    for rec in cashflow_records:
        normalized_cashflow.append(
            {
                "operating_cash_flow": _safe_get(
                    rec, "Total Cash From Operating Activities"
                ),
                "capital_expenditure": _safe_get(rec, "Capital Expenditures"),
                "free_cash_flow": _safe_get(rec, "Free Cash Flow"),
            }
        )

    return {
        "income_statement": normalized_income,
        "balance_sheet": normalized_balance,
        "cash_flow": normalized_cashflow,
        "source": "yfinance",
        "as_of_date": date.today().isoformat(),
    }
