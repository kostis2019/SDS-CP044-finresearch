# schemas/__init__.py
# Pydantic schemas for FinResearch agents
# ---------------------------------------------

from schemas.analyst_schemas import (
    AnalystOutput,
    CompanyProfile,
    TechnicalIndicators,
    FundamentalMetrics,
    GrowthMetrics,
    ProfitabilityMetrics,
    FinancialHealthMetrics,
    SectorBenchmarks,
    InvestmentScores,
)

from schemas.researcher_schemas import (
    ResearcherOutput,
    SentimentScore,
    NewsArticle,
    ResearcherOutputEmpty,
)

from schemas.reporter_schemas import (
    ReportOutput,
    TargetPrice,
    ScoreInterpretation,
    ExecutiveSummary,
    RecommendationRationale,
    CombinedAnalysisOutput,
)

__all__ = [
    # Analyst schemas
    "AnalystOutput",
    "CompanyProfile",
    "TechnicalIndicators",
    "FundamentalMetrics",
    "GrowthMetrics",
    "ProfitabilityMetrics",
    "FinancialHealthMetrics",
    "SectorBenchmarks",
    "InvestmentScores",
    # Researcher schemas
    "ResearcherOutput",
    "SentimentScore",
    "NewsArticle",
    "ResearcherOutputEmpty",
    # Reporter schemas
    "ReportOutput",
    "TargetPrice",
    "ScoreInterpretation",
    "ExecutiveSummary",
    "RecommendationRationale",
    "CombinedAnalysisOutput",
]
