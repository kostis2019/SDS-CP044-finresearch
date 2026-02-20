# schemas/alternative_data_schemas.py
# Pydantic schemas for Alternative Data (Phase 1)
# Insider Transactions, Analyst Recommendations, Institutional Ownership
# ---------------------------------------------

from pydantic import BaseModel, Field
from typing import Optional, List, Literal


class InsiderTransaction(BaseModel):
    """Single insider transaction record."""
    insider_name: Optional[str] = Field(None, description="Name of insider")
    title: Optional[str] = Field(None, description="Title/position of insider")
    transaction_type: Optional[Literal["Buy", "Sell", "Other"]] = Field(None, description="Transaction type")
    shares: Optional[int] = Field(None, description="Number of shares")
    value: Optional[float] = Field(None, description="Transaction value in USD")
    date: Optional[str] = Field(None, description="Transaction date")


class InsiderSummary(BaseModel):
    """Summary of insider transaction activity."""
    total_buys: int = Field(default=0, description="Total buy transactions")
    total_sells: int = Field(default=0, description="Total sell transactions")
    net_value: float = Field(default=0, description="Net value (buys - sells)")
    buy_sell_ratio: float = Field(default=0, description="Ratio of buys to sells")
    insider_sentiment: Literal["Bullish", "Neutral", "Bearish"] = Field(
        default="Neutral", description="Overall insider sentiment"
    )


class InsiderData(BaseModel):
    """Complete insider transaction data."""
    status: Literal["success", "no_data", "error"] = Field(default="no_data")
    ticker: str = Field(..., description="Stock ticker")
    transactions: List[InsiderTransaction] = Field(default_factory=list)
    summary: InsiderSummary = Field(default_factory=InsiderSummary)
    message: Optional[str] = Field(None, description="Status message or error")


class TargetPrices(BaseModel):
    """Analyst price target data."""
    low: Optional[float] = Field(None, description="Low price target")
    mean: Optional[float] = Field(None, description="Mean price target")
    median: Optional[float] = Field(None, description="Median price target")
    high: Optional[float] = Field(None, description="High price target")


class RecommendationCounts(BaseModel):
    """Count of analyst recommendations by rating."""
    strong_buy: int = Field(default=0)
    buy: int = Field(default=0)
    hold: int = Field(default=0)
    sell: int = Field(default=0)
    strong_sell: int = Field(default=0)


class RecentChange(BaseModel):
    """Recent analyst rating change."""
    firm: Optional[str] = Field(None, description="Analyst firm name")
    to_grade: Optional[str] = Field(None, description="New rating")
    from_grade: Optional[str] = Field(None, description="Previous rating")
    action: Optional[str] = Field(None, description="Action type (upgrade/downgrade)")
    date: Optional[str] = Field(None, description="Date of change")


class AnalystData(BaseModel):
    """Complete analyst recommendation data."""
    status: Literal["success", "no_data", "error"] = Field(default="no_data")
    ticker: str = Field(..., description="Stock ticker")
    current_price: Optional[float] = Field(None, description="Current stock price")
    target_prices: TargetPrices = Field(default_factory=TargetPrices)
    upside_percent: float = Field(default=0, description="Upside to mean target (%)")
    recommendations: RecommendationCounts = Field(default_factory=RecommendationCounts)
    consensus: str = Field(default="No Data", description="Consensus rating")
    total_analysts: int = Field(default=0, description="Number of analysts covering")
    recent_changes: List[RecentChange] = Field(default_factory=list)


class InstitutionalHolder(BaseModel):
    """Single institutional holder record."""
    holder: Optional[str] = Field(None, description="Institution name")
    shares: Optional[int] = Field(None, description="Shares held")
    value: Optional[float] = Field(None, description="Value of holdings")
    percent_held: Optional[float] = Field(None, description="Percentage of float held")
    date_reported: Optional[str] = Field(None, description="Date of filing")


class InstitutionalSummary(BaseModel):
    """Summary of institutional ownership."""
    total_institutional_shares: int = Field(default=0)
    num_institutions: int = Field(default=0)
    concentration: Literal["High", "Medium", "Low", "Unknown"] = Field(default="Unknown")


class InstitutionalData(BaseModel):
    """Complete institutional ownership data."""
    status: Literal["success", "no_data", "error"] = Field(default="no_data")
    ticker: str = Field(..., description="Stock ticker")
    institutional_ownership_percent: Optional[float] = Field(
        None, description="Percentage held by institutions"
    )
    top_holders: List[InstitutionalHolder] = Field(default_factory=list)
    summary: InstitutionalSummary = Field(default_factory=InstitutionalSummary)


class ValuationMetrics(BaseModel):
    """Enhanced valuation metrics (Phase 1)."""
    status: Literal["success", "partial", "error"] = Field(default="partial")
    ticker: str = Field(..., description="Stock ticker")
    current_price: Optional[float] = Field(None)
    market_cap: Optional[float] = Field(None)
    enterprise_value: Optional[float] = Field(None)
    
    # Traditional Ratios
    pe_ttm: Optional[float] = Field(None, description="Trailing P/E ratio")
    pe_forward: Optional[float] = Field(None, description="Forward P/E ratio")
    peg_ratio: Optional[float] = Field(None, description="PEG ratio")
    price_to_book: Optional[float] = Field(None, description="Price to book ratio")
    price_to_sales: Optional[float] = Field(None, description="Price to sales ratio")
    
    # Enterprise Value Ratios (NEW)
    ev_to_ebitda: Optional[float] = Field(None, description="EV/EBITDA ratio")
    ev_to_revenue: Optional[float] = Field(None, description="EV/Revenue ratio")
    ev_to_fcf: Optional[float] = Field(None, description="EV/Free Cash Flow ratio")
    
    # Cash Flow Based (NEW)
    free_cash_flow: Optional[float] = Field(None, description="Free cash flow")
    fcf_yield: Optional[float] = Field(None, description="FCF Yield (%)")
    fcf_per_share: Optional[float] = Field(None, description="FCF per share")
    price_to_fcf: Optional[float] = Field(None, description="Price to FCF ratio")
    earnings_yield: Optional[float] = Field(None, description="Earnings yield (%)")
    
    # Dividend
    dividend_yield: Optional[float] = Field(None, description="Dividend yield (%)")
    payout_ratio: Optional[float] = Field(None, description="Dividend payout ratio (%)")
    
    # Assessment
    valuation_label: Literal["Undervalued", "Fair Value", "Overvalued", "Unknown"] = Field(
        default="Unknown", description="Valuation assessment"
    )
    valuation_score: float = Field(default=50, ge=0, le=100, description="Valuation score (0-100)")


class AlternativeData(BaseModel):
    """Combined alternative data for a stock."""
    ticker: str = Field(..., description="Stock ticker")
    insider_transactions: InsiderData = Field(default_factory=lambda: InsiderData(ticker=""))
    analyst_recommendations: AnalystData = Field(default_factory=lambda: AnalystData(ticker=""))
    institutional_ownership: InstitutionalData = Field(default_factory=lambda: InstitutionalData(ticker=""))
    valuation_metrics: ValuationMetrics = Field(default_factory=lambda: ValuationMetrics(ticker=""))
