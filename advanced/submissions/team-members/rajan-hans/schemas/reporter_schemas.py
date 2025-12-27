# schemas/reporter_schemas.py
# Pydantic schemas for Reporter Agent outputs
# These enforce strict typing and validation to reduce hallucinations
# Made resilient with sensible defaults to prevent validation errors
# ---------------------------------------------

from pydantic import BaseModel, Field, field_validator
from typing import List, Literal, Optional, Union
from datetime import date


class TargetPrice(BaseModel):
    """Target price range calculation."""
    status: Literal["Computed", "Not available"] = Field(
        default="Not available", description="Whether target price could be computed"
    )
    current_price: Optional[float] = Field(None, ge=0, description="Current stock price")
    range_low: Optional[float] = Field(None, ge=0, description="Lower bound of target range")
    range_high: Optional[float] = Field(None, ge=0, description="Upper bound of target range")
    method: Optional[str] = Field(None, description="Methodology used for calculation")


class ScoreInterpretation(BaseModel):
    """Interpretation of a single factor score."""
    name: str = Field(default="Unknown", description="Factor name (e.g., Valuation, Growth)")
    score: Optional[float] = Field(default=None, ge=0, le=100, description="Score value (0-100)")
    interpretation: str = Field(default="Score not available", description="Human-readable interpretation")
    
    @field_validator('score', mode='before')
    @classmethod
    def parse_score(cls, v):
        """Convert string scores to float, handle 'Not available' gracefully."""
        if v is None:
            return None
        if isinstance(v, (int, float)):
            return float(v)
        if isinstance(v, str):
            # Handle "Not available" or similar strings
            v_lower = v.lower().strip()
            if v_lower in ('not available', 'n/a', 'na', 'none', '-', ''):
                return None
            try:
                return float(v)
            except ValueError:
                return None
        return None


class ExecutiveSummary(BaseModel):
    """Structured executive summary."""
    investment_thesis: str = Field(
        default="Analysis in progress.", 
        description="One-sentence investment thesis"
    )
    key_points: List[str] = Field(
        default_factory=list,
        description="3-7 key bullet points"
    )


class RecommendationRationale(BaseModel):
    """Structured recommendation explanation."""
    summary: str = Field(
        default="See full report for details.", 
        description="Brief recommendation summary"
    )
    supporting_factors: List[str] = Field(
        default_factory=list,
        description="Factors supporting the recommendation"
    )
    concerns: List[str] = Field(
        default_factory=list, 
        description="Factors of concern"
    )


class ReportOutput(BaseModel):
    """
    Complete output schema for the Reporter Agent.
    This schema enforces strict typing to prevent hallucinations.
    
    The Reporter must ONLY use data provided by the Analyst and Researcher.
    If data is missing, fields should be marked as "Not available".
    
    Made resilient with sensible defaults to prevent validation errors when
    the LLM doesn't provide all required fields.
    """
    ticker: str = Field(..., description="Stock ticker symbol")
    
    as_of_date: str = Field(
        default_factory=lambda: date.today().isoformat(), 
        description="Report generation date"
    )
    
    sector: str = Field(default="Unknown", description="Company sector")
    
    final_score: float = Field(
        default=50.0, 
        ge=0, 
        le=100, 
        description="Final investment score (0-100)"
    )
    
    rating_5_tier: Literal["STRONG BUY", "BUY", "HOLD", "REDUCE", "SELL"] = Field(
        default="HOLD", 
        description="5-tier investment rating"
    )
    
    confidence: Literal["HIGH", "MEDIUM", "LOW"] = Field(
        default="MEDIUM", 
        description="Confidence level in the analysis"
    )
    
    risk_level: Literal["HIGH", "MEDIUM", "LOW"] = Field(
        default="MEDIUM", 
        description="Overall risk assessment"
    )
    
    target_price: Optional[TargetPrice] = Field(
        default=None, 
        description="Target price range if calculable"
    )
    
    executive_summary: ExecutiveSummary = Field(
        default_factory=ExecutiveSummary, 
        description="Executive summary section"
    )
    
    score_interpretations: List[ScoreInterpretation] = Field(
        default_factory=list,
        description="Interpretation of each factor score"
    )
    
    recommendation_rationale: RecommendationRationale = Field(
        default_factory=RecommendationRationale, 
        description="Detailed recommendation rationale"
    )
    
    key_risks: List[str] = Field(
        default_factory=list, 
        description="Key risk factors"
    )
    
    key_opportunities: List[str] = Field(
        default_factory=list, 
        description="Key opportunities/catalysts"
    )
    
    report_markdown: str = Field(
        default="Report generation incomplete. Please check the Debug Output tab for raw data.", 
        description="Full markdown report text"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "ticker": "AAPL",
                "as_of_date": "2025-12-25",
                "sector": "Technology",
                "final_score": 72.5,
                "rating_5_tier": "BUY",
                "confidence": "HIGH",
                "risk_level": "LOW",
                "executive_summary": {
                    "investment_thesis": "Apple remains a strong buy due to robust services growth.",
                    "key_points": [
                        "Strong profitability metrics",
                        "Healthy balance sheet",
                        "Growing services revenue"
                    ]
                },
                "recommendation_rationale": {
                    "summary": "Buy rating supported by strong fundamentals",
                    "supporting_factors": ["High ROE", "Low debt"],
                    "concerns": ["China exposure"]
                },
                "report_markdown": "# Equity Research Report..."
            }
        }


class CombinedAnalysisOutput(BaseModel):
    """
    Combined output containing all agent outputs.
    Used for the final result returned to the application.
    All fields have defaults to ensure the app always gets usable data.
    """
    # Report data
    ticker: str = Field(default="UNKNOWN")
    as_of_date: str = Field(default_factory=lambda: date.today().isoformat())
    sector: str = Field(default="Unknown")
    final_score: Optional[float] = Field(default=None)
    rating_5_tier: Optional[str] = Field(default=None)
    confidence: Optional[str] = Field(default=None)
    risk_level: Optional[str] = Field(default=None)
    report_markdown: str = Field(default="Report not available.")
    
    # Analyst data (preserved for display)
    scores: Optional[dict] = Field(default=None)
    technical_indicators: Optional[dict] = Field(default=None)
    fundamental_metrics: Optional[dict] = Field(default=None)
    company_profile: Optional[dict] = Field(default=None)
    sector_benchmarks: Optional[dict] = Field(default=None)
    analyst_summary: Optional[List[str]] = Field(default=None)
    
    # Researcher data (preserved for display)
    headline_summary: Optional[List[str]] = Field(default=None)
    sentiment: Optional[dict] = Field(default=None)
    key_risks: Optional[List[str]] = Field(default=None)
    key_tailwinds: Optional[List[str]] = Field(default=None)
    news_source: Optional[str] = Field(default=None)
    
    # Metadata
    execution_info: Optional[dict] = Field(default=None)
    raw_sector: Optional[str] = Field(default=None)
    
    # Error tracking
    report_parse_error: Optional[str] = Field(default=None)
    analyst_parse_error: Optional[str] = Field(default=None)
    researcher_parse_error: Optional[str] = Field(default=None)
