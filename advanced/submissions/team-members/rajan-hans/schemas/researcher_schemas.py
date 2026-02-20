# schemas/researcher_schemas.py
# Pydantic schemas for Researcher Agent outputs
# These enforce strict typing and validation to reduce hallucinations
# ---------------------------------------------

from pydantic import BaseModel, Field
from typing import List, Literal, Optional


class SentimentScore(BaseModel):
    """Sentiment analysis result."""
    label: Literal["Positive", "Neutral", "Negative"] = Field(
        ..., description="Overall sentiment classification"
    )
    score: float = Field(
        ..., 
        ge=-1.0, 
        le=1.0, 
        description="Sentiment score from -1 (very negative) to +1 (very positive)"
    )


class NewsArticle(BaseModel):
    """Individual news article metadata."""
    title: str = Field(..., description="Article headline")
    source: Optional[str] = Field(None, description="Publication source URL")
    summary: Optional[str] = Field(None, description="Brief article summary")


class ResearcherOutput(BaseModel):
    """
    Complete output schema for the Researcher Agent.
    This schema enforces strict typing to prevent hallucinations.
    
    The Researcher must ONLY include information retrieved from news search tools.
    Empty lists are acceptable if no news is found.
    Made resilient with sensible defaults.
    """
    ticker: str = Field(..., description="Stock ticker symbol")
    
    headline_summary: List[str] = Field(
        default_factory=list,
        description="3-5 key headlines/developments derived from actual news articles"
    )
    
    sentiment: SentimentScore = Field(
        default_factory=lambda: SentimentScore(label="Neutral", score=0.0),
        description="Overall market sentiment based on news coverage"
    )
    
    key_risks: List[str] = Field(
        default_factory=list,
        description="Key risk factors mentioned in recent news coverage"
    )
    
    key_tailwinds: List[str] = Field(
        default_factory=list,
        description="Key positive catalysts mentioned in recent news coverage"
    )
    
    news_source: Literal["tavily", "serpapi", "none"] = Field(
        default="none", 
        description="Which news API provided the data"
    )
    
    articles_analyzed: Optional[int] = Field(
        None, 
        ge=0, 
        description="Number of news articles analyzed"
    )
    
    search_query: Optional[str] = Field(
        None, 
        description="The search query used to find news"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "ticker": "AAPL",
                "headline_summary": [
                    "Apple reports record Q4 earnings beating analyst expectations",
                    "iPhone 16 sales exceed forecasts in key markets",
                    "Services revenue continues double-digit growth"
                ],
                "sentiment": {
                    "label": "Positive",
                    "score": 0.65
                },
                "key_risks": [
                    "China market weakness amid economic slowdown",
                    "Regulatory scrutiny in EU markets"
                ],
                "key_tailwinds": [
                    "Strong services growth providing recurring revenue",
                    "AI features driving upgrade cycle"
                ],
                "news_source": "tavily",
                "articles_analyzed": 5
            }
        }


class ResearcherOutputEmpty(BaseModel):
    """
    Schema for when no news is found.
    This prevents the LLM from making up news.
    """
    ticker: str = Field(..., description="Stock ticker symbol")
    headline_summary: List[str] = Field(default_factory=list)
    sentiment: SentimentScore = Field(
        default_factory=lambda: SentimentScore(label="Neutral", score=0.0)
    )
    key_risks: List[str] = Field(default_factory=list)
    key_tailwinds: List[str] = Field(default_factory=list)
    news_source: Literal["none"] = Field(default="none")
    error_message: Optional[str] = Field(
        None, 
        description="Explanation of why no news was found"
    )
