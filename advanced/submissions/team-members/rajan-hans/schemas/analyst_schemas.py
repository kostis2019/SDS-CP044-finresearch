# schemas/analyst_schemas.py
# Pydantic schemas for Analyst Agent outputs
# These enforce strict typing and validation to reduce hallucinations
# ---------------------------------------------

from pydantic import BaseModel, Field, model_validator
from typing import Optional, List, Literal, Any
from datetime import date


class CompanyProfile(BaseModel):
    """Company profile information from Yahoo Finance."""

    company_name: Optional[str] = Field(None, description="Short company name")
    long_name: Optional[str] = Field(None, description="Full legal company name")
    exchange: Optional[str] = Field(
        None, description="Stock exchange (e.g., NYSE, NASDAQ)"
    )
    industry: Optional[str] = Field(None, description="Industry classification")
    sector: Optional[str] = Field(None, description="Sector classification")
    market_cap: Optional[float] = Field(
        None, description="Market capitalization in USD"
    )
    currency: Optional[str] = Field(None, description="Reporting currency")
    country: Optional[str] = Field(None, description="Country of headquarters")
    website: Optional[str] = Field(None, description="Company website URL")
    pe_ttm: Optional[float] = Field(None, description="Trailing 12-month P/E ratio")
    forward_pe: Optional[float] = Field(None, description="Forward P/E ratio")
    peg_ratio: Optional[float] = Field(None, description="PEG ratio")
    price_to_book: Optional[float] = Field(None, description="Price to book ratio")
    roe: Optional[float] = Field(None, description="Return on equity")
    debt_to_equity: Optional[float] = Field(None, description="Debt to equity ratio")
    dividend_yield: Optional[float] = Field(
        None, description="Dividend yield percentage"
    )
    beta: Optional[float] = Field(None, description="Beta coefficient")
    week_52_high: Optional[float] = Field(
        None, alias="52_week_high", description="52-week high price"
    )
    week_52_low: Optional[float] = Field(
        None, alias="52_week_low", description="52-week low price"
    )
    current_price: Optional[float] = Field(None, description="Current stock price")

    class Config:
        populate_by_name = True


# --- NEW CLASS ADDED HERE ---
class MarketConsensus(BaseModel):
    """Analyst ratings and price targets."""

    target_price_mean: Optional[float] = Field(
        None, description="Mean analyst price target"
    )
    target_price_high: Optional[float] = Field(
        None, description="High analyst price target"
    )
    target_price_low: Optional[float] = Field(
        None, description="Low analyst price target"
    )
    consensus: Optional[str] = Field(
        None, description="Consensus rating (e.g. Buy, Hold)"
    )
    recommendation_counts: Optional[dict] = Field(None, description="Count of ratings")


class TechnicalIndicators(BaseModel):
    """Technical analysis indicators computed from price data. Phase 1 Enhanced."""

    # Moving Averages
    sma20: Optional[float] = Field(None, description="20-day simple moving average")
    sma50: Optional[float] = Field(None, description="50-day simple moving average")
    sma200: Optional[float] = Field(None, description="200-day simple moving average")
    # RSI
    rsi14: Optional[float] = Field(None, ge=0, le=100, description="14-day RSI (0-100)")
    # MACD
    macd: Optional[float] = Field(None, description="MACD line value")
    macd_signal: Optional[float] = Field(None, description="MACD signal line value")
    macd_hist: Optional[float] = Field(None, description="MACD histogram value")
    # Volatility
    volatility_30d: Optional[float] = Field(
        None, ge=0, description="30-day annualized volatility"
    )
    max_drawdown_1y: Optional[float] = Field(
        None, description="Maximum drawdown in past year (negative)"
    )
    # Bollinger Bands (NEW)
    bb_upper: Optional[float] = Field(None, description="Upper Bollinger Band")
    bb_middle: Optional[float] = Field(
        None, description="Middle Bollinger Band (SMA20)"
    )
    bb_lower: Optional[float] = Field(None, description="Lower Bollinger Band")
    bb_width: Optional[float] = Field(
        None, description="Bollinger Band width (volatility)"
    )
    bb_percent: Optional[float] = Field(
        None, description="Price position within bands (0-1)"
    )
    # ATR (NEW)
    atr14: Optional[float] = Field(None, description="14-day Average True Range")
    atr_percent: Optional[float] = Field(None, description="ATR as percentage of price")
    # Stochastic Oscillator (NEW)
    stoch_k: Optional[float] = Field(None, ge=0, le=100, description="Stochastic %K")
    stoch_d: Optional[float] = Field(None, ge=0, le=100, description="Stochastic %D")
    # 52-Week Position (NEW)
    week_52_high: Optional[float] = Field(None, description="52-week high price")
    week_52_low: Optional[float] = Field(None, description="52-week low price")
    week_52_position: Optional[float] = Field(
        None, ge=0, le=100, description="Position in 52-week range (%)"
    )
    # Labels
    trend_label: Optional[Literal["uptrend", "downtrend", "sideways"]] = Field(
        None, description="Current price trend"
    )
    momentum_label: Optional[Literal["bullish", "bearish", "neutral"]] = Field(
        None, description="Current momentum signal"
    )
    volatility_label: Optional[Literal["high", "moderate", "low"]] = Field(
        None, description="Volatility level assessment"
    )
    bb_signal: Optional[Literal["overbought", "oversold", "squeeze", "neutral"]] = (
        Field(None, description="Bollinger Band signal")
    )


class GrowthMetrics(BaseModel):
    """Growth-related fundamental metrics."""

    revenue_cagr_3y: Optional[float] = Field(None, description="3-year revenue CAGR")
    eps_cagr_3y: Optional[float] = Field(None, description="3-year EPS CAGR")
    revenue_yoy: Optional[float] = Field(
        None, description="Year-over-year revenue growth"
    )
    eps_yoy: Optional[float] = Field(None, description="Year-over-year EPS growth")
    growth_trend: Optional[Literal["accelerating", "stable", "slowing", "unknown"]] = (
        Field(None, description="Overall growth trend assessment")
    )


class ProfitabilityMetrics(BaseModel):
    """Profitability-related fundamental metrics."""

    gross_margin: Optional[float] = Field(None, description="Gross profit margin")
    operating_margin: Optional[float] = Field(
        None, description="Operating profit margin"
    )
    net_margin: Optional[float] = Field(None, description="Net profit margin")
    roe: Optional[float] = Field(None, description="Return on equity")
    roa: Optional[float] = Field(None, description="Return on assets")
    profitability_level: Optional[Literal["high", "medium", "low", "unknown"]] = Field(
        None, description="Overall profitability assessment"
    )


class FinancialHealthMetrics(BaseModel):
    """Financial health and balance sheet metrics."""

    # Note: debt_equity CAN be negative for companies with negative equity (e.g., accumulated losses)
    debt_equity: Optional[float] = Field(
        None, description="Debt to equity ratio (can be negative)"
    )
    interest_coverage: Optional[float] = Field(
        None, description="Interest coverage ratio (can be negative)"
    )
    cash_to_debt: Optional[float] = Field(None, description="Cash to debt ratio")
    current_ratio: Optional[float] = Field(None, description="Current ratio")
    balance_sheet_strength: Optional[
        Literal["strong", "acceptable", "weak", "unknown"]
    ] = Field(None, description="Overall balance sheet assessment")


class FundamentalMetrics(BaseModel):
    """Combined fundamental metrics."""

    growth: GrowthMetrics = Field(default_factory=GrowthMetrics)
    profitability: ProfitabilityMetrics = Field(default_factory=ProfitabilityMetrics)
    financial_health: FinancialHealthMetrics = Field(
        default_factory=FinancialHealthMetrics
    )


class SectorBenchmarks(BaseModel):
    """Sector benchmark data for comparison."""

    sector: str = Field(..., description="Sector name")
    pe_median: Optional[float] = Field(None, description="Sector median P/E")
    forward_pe_median: Optional[float] = Field(
        None, description="Sector median forward P/E"
    )
    gross_margin_median: Optional[float] = Field(
        None, description="Sector median gross margin"
    )
    operating_margin_median: Optional[float] = Field(
        None, description="Sector median operating margin"
    )
    as_of_date: Optional[str] = Field(None, description="Benchmark data date")
    source: Optional[str] = Field(None, description="Data source")


class InvestmentScores(BaseModel):
    """Factor scores and final rating."""

    valuation_score: float = Field(
        default=50.0, ge=0, le=100, description="Valuation score (0-100)"
    )
    growth_score: float = Field(
        default=50.0, ge=0, le=100, description="Growth score (0-100)"
    )
    profitability_score: float = Field(
        default=50.0, ge=0, le=100, description="Profitability score (0-100)"
    )
    financial_health_score: float = Field(
        default=50.0, ge=0, le=100, description="Financial health score (0-100)"
    )
    technical_score: float = Field(
        default=50.0, ge=0, le=100, description="Technical score (0-100)"
    )
    composite_score: Optional[float] = Field(
        None, ge=0, le=100, description="Composite score before adjustments"
    )
    final_score: float = Field(
        default=50.0, ge=0, le=100, description="Final investment score (0-100)"
    )
    rating: Literal["STRONG BUY", "BUY", "HOLD", "REDUCE", "SELL"] = Field(
        default="HOLD", description="Investment rating based on final score"
    )


class AnalystOutput(BaseModel):
    """
    Complete output schema for the Analyst Agent.
    This schema enforces strict typing to prevent hallucinations.
    Made resilient with sensible defaults.
    
    Uses validators to handle None values that LLMs sometimes return,
    replacing them with sensible defaults instead of failing validation.
    """

    ticker: str = Field(..., description="Stock ticker symbol")
    sector: str = Field(default="Unknown", description="Company sector")
    as_of_date: str = Field(
        default_factory=lambda: date.today().isoformat(), description="Analysis date"
    )

    company_profile: Optional[CompanyProfile] = Field(
        default=None, description="Company information"
    )

    market_consensus: Optional[MarketConsensus] = Field(
        default=None, description="Analyst price targets and consensus ratings"
    )

    technical_indicators: Optional[TechnicalIndicators] = Field(
        default=None, description="Technical analysis"
    )
    fundamental_metrics: Optional[FundamentalMetrics] = Field(
        default=None, description="Fundamental analysis"
    )
    sector_benchmarks: Optional[SectorBenchmarks] = Field(
        default=None, description="Sector comparison data"
    )
    scores: Optional[InvestmentScores] = Field(
        default=None, description="Investment factor scores"
    )
    analyst_summary: List[str] = Field(
        default_factory=list, description="3-7 bullet points summarizing key findings"
    )

    @model_validator(mode="before")
    @classmethod
    def replace_none_with_defaults(cls, data: Any) -> Any:
        """Replace None values with default instances to prevent validation errors."""
        if isinstance(data, dict):
            # Replace None with default instances for required nested models
            if data.get("company_profile") is None:
                data["company_profile"] = {}
            if data.get("technical_indicators") is None:
                data["technical_indicators"] = {}
            if data.get("fundamental_metrics") is None:
                data["fundamental_metrics"] = {}
            if data.get("scores") is None:
                data["scores"] = {}
        return data

    class Config:
        json_schema_extra = {
            "example": {
                "ticker": "AAPL",
                "sector": "Technology",
                "as_of_date": "2025-12-25",
                "scores": {
                    "valuation_score": 65.0,
                    "growth_score": 72.0,
                    "profitability_score": 85.0,
                    "financial_health_score": 78.0,
                    "technical_score": 60.0,
                    "final_score": 72.0,
                    "rating": "Buy",
                },
                "analyst_summary": [
                    "Strong profitability with 85% score",
                    "Healthy balance sheet",
                    "Technical indicators suggest consolidation",
                ],
            }
        }
