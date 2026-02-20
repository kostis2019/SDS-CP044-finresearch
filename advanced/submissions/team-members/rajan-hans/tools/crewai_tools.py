# tools/crewai_tools.py
# CrewAI-compatible tool wrappers for all analysis tools
# These wrap the existing deterministic functions as CrewAI tools
# Note: load_dotenv() should be called at application entry point only
# ---------------------------------------------

import json
from typing import Optional
from crewai.tools import tool
from tools.yfinance_provider import get_yfinance_provider

# Import existing tool functions
from tools.price_tools import get_price_history
from tools.technical_indicators_tools import compute_technical_indicators
from tools.fundamentals_tools import get_fundamentals
from tools.fundamental_metrics_tools import compute_fundamental_metrics
from tools.factor_scoring_tools import compute_factor_scores
from tools.sector_benchmarks_tools import get_sector_benchmarks

# Import valuation and alternative data tools
from tools.valuation_tools import get_valuation_metrics, compare_valuation_to_sector
from tools.alternative_data_tools import (
    get_insider_transactions,
    get_analyst_recommendations,
    get_institutional_holders,
    get_all_alternative_data,
)


@tool("fetch_stock_price_history")
def fetch_stock_price_history(ticker: str, period: str = "1y") -> str:
    """
    Fetch historical OHLCV price data for a stock ticker.
    Returns price history as JSON string with date, open, high, low, close, volume.
    Use this tool to get price data before computing technical indicators.

    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL', 'GOOG', 'MSFT')
        period: Data lookback period (e.g., '6mo', '1y', '2y'). Default is '1y'.

    Returns:
        JSON string containing price history data or error message.
    """
    try:
        df = get_price_history(ticker, period=period)
        # Convert to JSON-serializable format
        records = df.to_dict(orient="records")
        # Convert datetime to string
        for rec in records:
            rec["date"] = str(rec["date"])
        return json.dumps(
            {
                "status": "success",
                "ticker": ticker,
                "period": period,
                "row_count": len(records),
                "data": records[-10:],  # Last 10 records for brevity
                "summary": {
                    "latest_close": records[-1]["close"] if records else None,
                    "earliest_date": records[0]["date"] if records else None,
                    "latest_date": records[-1]["date"] if records else None,
                },
            },
            indent=2,
        )
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


@tool("compute_technical_analysis")
def compute_technical_analysis(ticker: str) -> str:
    """
    Compute technical indicators for a stock including RSI, MACD, moving averages,
    volatility, max drawdown, trend and momentum labels.

    This tool automatically fetches price data and computes all technical indicators.

    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL', 'GOOG', 'MSFT')

    Returns:
        JSON string containing all technical indicators.
    """
    try:
        # Fetch price data first
        price_df = get_price_history(ticker, period="1y")

        # Compute technical indicators
        technicals = compute_technical_indicators(price_df)

        return json.dumps(
            {"status": "success", "ticker": ticker, "technical_indicators": technicals},
            indent=2,
        )
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


@tool("fetch_fundamental_data")
def fetch_fundamental_data(ticker: str) -> str:
    """
    Fetch fundamental financial data for a stock including income statement,
    balance sheet, and cash flow data from the last 4 years.

    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL', 'GOOG', 'MSFT')

    Returns:
        JSON string containing normalized fundamental data.
    """
    try:
        fundamentals = get_fundamentals(ticker)
        return json.dumps(
            {"status": "success", "ticker": ticker, "fundamentals": fundamentals},
            indent=2,
        )
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


@tool("compute_fundamental_metrics")
def compute_fundamental_metrics_tool(ticker: str) -> str:
    """
    Compute key fundamental metrics including growth rates (CAGR), profitability
    ratios (ROE, margins), and financial health indicators (debt/equity, coverage).

    This tool automatically fetches fundamental data and computes all metrics.

    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL', 'GOOG', 'MSFT')

    Returns:
        JSON string containing computed fundamental metrics.
    """
    try:
        # Fetch fundamentals first
        fundamentals_raw = get_fundamentals(ticker)

        # Compute metrics
        metrics = compute_fundamental_metrics(fundamentals_raw)

        return json.dumps(
            {"status": "success", "ticker": ticker, "fundamental_metrics": metrics},
            indent=2,
        )
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


@tool("get_sector_benchmark_data")
def get_sector_benchmark_data(ticker: str, sector: str) -> str:
    """
    Get sector benchmark medians for valuation and profitability comparison.
    Use this to compare a stock's metrics against its sector peers.

    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL')
        sector: Sector name (e.g., 'Technology', 'Healthcare', 'Financials')

    Returns:
        JSON string containing sector benchmark data.
    """
    try:
        benchmarks = get_sector_benchmarks(ticker=ticker, sector=sector)
        return json.dumps(
            {"status": "success", "ticker": ticker, "sector_benchmarks": benchmarks},
            indent=2,
        )
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


@tool("compute_investment_scores")
def compute_investment_scores(
    ticker: str, sector: str, sentiment_adjustment: float = 0.0
) -> str:
    """
    Compute comprehensive investment factor scores including valuation, growth,
    profitability, financial health, and technical scores. Also computes final
    composite score and investment rating.

    This is the main scoring tool that combines all analysis into actionable scores.

    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL')
        sector: Sector name for benchmark comparison (e.g., 'Technology')
        sentiment_adjustment: Optional sentiment adjustment (-5 to +5). Default is 0.

    Returns:
        JSON string containing all scores and final rating.
    """
    try:
        # Fetch all required data
        price_df = get_price_history(ticker, period="1y")
        technicals = compute_technical_indicators(price_df)
        fundamentals_raw = get_fundamentals(ticker)
        fundamental_metrics = compute_fundamental_metrics(fundamentals_raw)
        benchmarks = get_sector_benchmarks(ticker=ticker, sector=sector)

        # Compute scores
        scores = compute_factor_scores(
            fundamental_metrics=fundamental_metrics,
            technical_indicators=technicals,
            sector_benchmarks=benchmarks,
            sentiment_adjustment=sentiment_adjustment,
        )

        return json.dumps(
            {
                "status": "success",
                "ticker": ticker,
                "sector": sector,
                "scores": scores,
                "technical_indicators": technicals,
                "fundamental_metrics": fundamental_metrics,
                "sector_benchmarks": benchmarks,
            },
            indent=2,
        )
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


@tool("get_company_profile")
def get_company_profile(ticker: str) -> str:
    """
    Get company profile information including name, exchange, industry, sector,
    market cap, and key valuation ratios from Yahoo Finance.

    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL')

    Returns:
        JSON string containing company profile data.
    """
    try:
        provider = get_yfinance_provider()
        info = provider.get_info(ticker)

        profile = {
            "company_name": info.get("shortName"),
            "long_name": info.get("longName"),
            "exchange": info.get("exchange"),
            "industry": info.get("industry"),
            "sector": info.get("sector"),
            "market_cap": info.get("marketCap"),
            "currency": info.get("currency"),
            "country": info.get("country"),
            "website": info.get("website"),
            "pe_ttm": info.get("trailingPE"),
            "forward_pe": info.get("forwardPE"),
            "peg_ratio": info.get("pegRatio"),
            "price_to_book": info.get("priceToBook"),
            "roe": info.get("returnOnEquity"),
            "debt_to_equity": info.get("debtToEquity"),
            "dividend_yield": info.get("dividendYield"),
            "beta": info.get("beta"),
            "52_week_high": info.get("fiftyTwoWeekHigh"),
            "52_week_low": info.get("fiftyTwoWeekLow"),
            "current_price": info.get("currentPrice") or info.get("regularMarketPrice"),
        }

        return json.dumps(
            {"status": "success", "ticker": ticker, "profile": profile}, indent=2
        )
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


# =========================================================
# ENHANCED VALUATION & ALTERNATIVE DATA TOOLS
# =========================================================


@tool("get_enhanced_valuation")
def get_enhanced_valuation(ticker: str) -> str:
    """
    Get comprehensive valuation metrics including EV/EBITDA, FCF Yield,
    Price/Sales, earnings yield, and valuation assessment.

    This provides deeper valuation analysis beyond basic P/E ratios.

    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL')

    Returns:
        JSON string containing comprehensive valuation metrics and assessment.
    """
    try:
        valuation = get_valuation_metrics(ticker)
        return json.dumps(valuation, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


@tool("get_insider_activity")
def get_insider_activity(ticker: str) -> str:
    """
    Fetch recent insider transactions (buys/sells) for a stock.

    Insider buying can signal confidence from company executives,
    while heavy selling might indicate concerns.

    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL')

    Returns:
        JSON string containing insider transactions and sentiment summary.
    """
    try:
        insider_data = get_insider_transactions(ticker)
        return json.dumps(insider_data, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


@tool("get_analyst_ratings")
def get_analyst_ratings(ticker: str) -> str:
    """
    Fetch analyst recommendations, price targets, and consensus rating.

    Shows what Wall Street analysts think about the stock including
    buy/hold/sell recommendations and target prices.

    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL')

    Returns:
        JSON string containing analyst recommendations, price targets, and consensus.
    """
    try:
        analyst_data = get_analyst_recommendations(ticker)
        return json.dumps(analyst_data, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


@tool("get_institutional_ownership")
def get_institutional_ownership(ticker: str) -> str:
    """
    Fetch institutional ownership data including top holders.

    High institutional ownership often indicates professional investor confidence.
    Changes in ownership can signal shifting sentiment.

    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL')

    Returns:
        JSON string containing institutional ownership data and top holders.
    """
    try:
        inst_data = get_institutional_holders(ticker)
        return json.dumps(inst_data, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


@tool("get_comprehensive_stock_data")
def get_comprehensive_stock_data(ticker: str, sector: str) -> str:
    """
    Get ALL available data for a stock in one call - technical indicators,
    fundamentals, valuation metrics, insider activity, analyst ratings,
    and institutional ownership.

    Use this for a complete stock analysis instead of calling multiple tools.

    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL')
        sector: Sector name for benchmark comparison (e.g., 'Technology')

    Returns:
        JSON string containing comprehensive stock data from all sources.
    """
    try:
        # Fetch all data
        price_df = get_price_history(ticker, period="1y")
        technicals = compute_technical_indicators(price_df)
        fundamentals_raw = get_fundamentals(ticker)
        fundamental_metrics = compute_fundamental_metrics(fundamentals_raw)
        benchmarks = get_sector_benchmarks(ticker=ticker, sector=sector)
        scores = compute_factor_scores(
            fundamental_metrics=fundamental_metrics,
            technical_indicators=technicals,
            sector_benchmarks=benchmarks,
        )

        # Alternative data
        valuation = get_valuation_metrics(ticker)
        insider_data = get_insider_transactions(ticker)
        analyst_data = get_analyst_recommendations(ticker)
        inst_data = get_institutional_holders(ticker)

        return json.dumps(
            {
                "status": "success",
                "ticker": ticker,
                "sector": sector,
                # Scores
                "scores": scores,
                # Technical Analysis
                "technical_indicators": technicals,
                # Fundamental Analysis
                "fundamental_metrics": fundamental_metrics,
                "sector_benchmarks": benchmarks,
                # Valuation
                "valuation_metrics": valuation,
                # Alternative Data
                "insider_transactions": insider_data,
                "analyst_recommendations": analyst_data,
                "institutional_ownership": inst_data,
            },
            indent=2,
            default=str,
        )
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


# Export all tools for easy import
ANALYST_TOOLS = [
    # Original tools
    fetch_stock_price_history,
    compute_technical_analysis,
    fetch_fundamental_data,
    compute_fundamental_metrics_tool,
    get_sector_benchmark_data,
    compute_investment_scores,
    get_company_profile,
    # Enhanced tools
    get_enhanced_valuation,
    get_insider_activity,
    get_analyst_ratings,
    get_institutional_ownership,
    get_comprehensive_stock_data,
]


# Convenience export for alternative data tools
ALTERNATIVE_DATA_TOOLS = [
    get_enhanced_valuation,
    get_insider_activity,
    get_analyst_ratings,
    get_institutional_ownership,
]
