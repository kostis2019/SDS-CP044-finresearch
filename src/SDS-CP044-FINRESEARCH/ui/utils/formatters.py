"""
Utilities for formatting and parsing crew outputs.
"""

from typing import Any, Dict


def parse_crew_output(crew_result: Any, user_inputs: dict) -> dict:
    """
    Parse CrewAI output into structured format for UI display.
    
    Args:
        crew_result: Raw output from crew.kickoff()
        user_inputs: Original user input parameters
        
    Returns:
        dict: Structured results for UI rendering
    """
    
    # Convert crew result to string if needed
    result_text = str(crew_result)
    
    # This is a placeholder - you'll need to parse based on your actual crew output format
    # The structure below shows the expected format for the UI
    
    structured_results = {
        "ticker": user_inputs.get("ticker"),
        "investor_mode": user_inputs.get("investor_mode"),
        "timestamp": user_inputs.get("timestamp"),
        
        "executive_summary": extract_executive_summary(result_text),
        "financial_indicators": extract_financial_indicators(result_text),
        "news_sentiment": extract_news_sentiment(result_text),
        "risks_opportunities": extract_risks_opportunities(result_text),
        "full_report": result_text
    }
    
    return structured_results


def extract_executive_summary(text: str) -> dict:
    """Extract executive summary data from crew output."""
    
    # TODO: Implement actual parsing logic based on your crew's output format
    return {
        "current_price": "N/A",
        "price_change": "N/A",
        "recommendation": "Hold",
        "risk_level": "Medium",
        "key_takeaways": "Analysis in progress...",
        "investment_thesis": "Detailed analysis pending..."
    }


def extract_financial_indicators(text: str) -> dict:
    """Extract financial indicators from crew output."""
    
    # TODO: Implement actual parsing logic
    return {
        "pe_ratio": "N/A",
        "peg_ratio": "N/A",
        "pb_ratio": "N/A",
        "ev_ebitda": "N/A",
        "roe": "N/A",
        "roa": "N/A",
        "profit_margin": "N/A",
        "operating_margin": "N/A",
        "beta": "N/A",
        "volatility": "N/A",
        "sharpe_ratio": "N/A",
        "growth_data": []
    }


def extract_news_sentiment(text: str) -> dict:
    """Extract news and sentiment data from crew output."""
    
    # TODO: Implement actual parsing logic
    return {
        "sentiment_score": 0.0,
        "sentiment_trend": "Neutral",
        "news_count": 0,
        "social_mentions": "N/A",
        "news_items": [],
        "analyst_ratings": {}
    }


def extract_risks_opportunities(text: str) -> dict:
    """Extract risks and opportunities from crew output."""
    
    # TODO: Implement actual parsing logic
    return {
        "opportunities": [],
        "risks": [],
        "swot": {
            "strengths": [],
            "weaknesses": [],
            "opportunities": [],
            "threats": []
        }
    }