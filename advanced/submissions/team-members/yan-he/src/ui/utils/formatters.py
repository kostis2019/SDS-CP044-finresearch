"""
Utilities for formatting and parsing crew outputs.
"""

from typing import Any, List
import json
import re

def parse_crew_output(crew_result: Any, user_inputs: dict) -> dict:
    """
    Parse CrewAI output into structured format for UI display.
    
    Args:
        crew_result: Raw output from crew.kickoff() (JSON string or dict)
        user_inputs: Original user input parameters
        
    Returns:
        dict: Structured results for UI rendering
    """
    
    # Convert crew result to string if needed
    result_text = str(crew_result)
    
    # Try to parse as JSON
    try:
        # If it's already a dict, use it directly
        if isinstance(crew_result, dict):
            report_data = crew_result
        else:
            # Try to extract JSON from the text
            # Look for JSON content between { and }
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                report_data = json.loads(json_str)
            else:
                # Fallback to parsing the text
                report_data = {}
    except (json.JSONDecodeError, AttributeError) as e:
        print(f"Warning: Could not parse JSON from crew result: {e}")
        # Fallback to empty structure
        report_data = {}
    
    structured_results = {
        "ticker": user_inputs.get("ticker"),
        "investor_mode": user_inputs.get("investor_mode"),
        "timestamp": user_inputs.get("timestamp"),
        
        "executive_summary": extract_executive_summary(report_data),
        "financial_indicators": extract_financial_indicators(report_data),
        "news_sentiment": extract_news_sentiment(report_data),
        "risks_opportunities": extract_risks_opportunities(report_data),
        "full_report": report_data.get("Full Report", result_text)
    }
    
    return structured_results


def extract_executive_summary(report_data: dict) -> dict:
    """
    Extract executive summary data from JSON report.
    
    Args:
        report_data: Parsed JSON report data
        
    Returns:
        dict: Executive summary with key metrics
    """  
    
    exec_summary_text = report_data.get("Executive Summary", "")
    financial_indicators = report_data.get("Financial Indicators", {})  
    
    # Extract price information
    price_movements = financial_indicators.get("Price Movements", {})
    current_price = price_movements.get("Current Price", "N/A")   
    
    # Format current price
    if current_price:
        if isinstance(current_price, (int, float)):
            current_price_str = f"${current_price:.2f}"
        else:
            current_price_str = str(current_price)
    if isinstance(price_movements, str):
        current_price_str = price_movements
    
    # Calculate price change
    monthly_return = price_movements.get("Monthly Return", 0)
    if isinstance(monthly_return, (int, float)):
        price_change = f"+{monthly_return:.1f}%" if monthly_return > 0 else f"{monthly_return:.1f}%"
    else:
        price_change = "N/A"
    
    # Extract 52-week range
    week_52_range = price_movements.get("52-Week Range", [])
    if len(week_52_range) == 2:
        #range_str = f"${week_52_range[0]:.2f} - ${week_52_range[1]:.2f}"
        range_str = f"${week_52_range[0]} - ${week_52_range[1]}"
    elif len(week_52_range) == 0:
        week_52_high = price_movements.get("52-Week High", "")
        week_52_low = price_movements.get("52-Week Low", "")
        range_str = f"${week_52_low} - ${week_52_high}"

    else:
        range_str = "N/A"
    
    # Determine recommendation from sentiment
    recommendation = determine_recommendation(exec_summary_text, report_data)
    
    # Assess risk level
    risk_level = assess_risk_level(report_data)
    
    # Extract market cap from Full Report or Financial Indicators
    market_cap = extract_market_cap(report_data)
    
    return {
        "current_price": current_price_str,
        "price_change": price_change,
        "52_week_range": range_str,
        "market_cap": market_cap,
        "recommendation": recommendation,
        "risk_level": risk_level,
        "key_takeaways": exec_summary_text,
        "investment_thesis": exec_summary_text
    }


def extract_financial_indicators(report_data: dict) -> dict:
    """
    Extract financial indicators from JSON report.
    
    Args:
        report_data: Parsed JSON report data
        
    Returns:
        dict: Financial metrics and ratios
    """
    
    financial_indicators = report_data.get("Financial Indicators", {})
    
    # Extract price movements
    price_movements = financial_indicators.get("Price Movements", {})
    current_price = price_movements.get('Current Price', 0)   

    week_52_range = price_movements.get("52-Week Range", [])
    
    high_52w = f"${week_52_range[1]:.2f}" if len(week_52_range) == 2 else "N/A"
    low_52w = f"${week_52_range[0]:.2f}" if len(week_52_range) == 2 else "N/A"
    
    # Extract valuation ratios
    valuation_ratios = financial_indicators.get("Valuation Ratios", {})
    if isinstance(valuation_ratios, dict):
        pe_ratio = valuation_ratios.get("P/E Ratio", "N/A") or \
                   valuation_ratios.get("Price-Earnings (P/E) Ratio", "N/A")
        peg_ratio = valuation_ratios.get("PEG Ratio", "N/A")
        pb_ratio = valuation_ratios.get("P/B Ratio", "N/A")
        #debt_to_equity = valuation_ratios.get("Debt/Equity Ratio", "N/A") or \
        #                valuation_ratios.get("Debt-to-Equity", "N/A")Revenue Growt
        debt_to_equity = valuation_ratios.get("Debt-to-Equity", "N/A")
    
    # Extract profitability ratios
    profitability_ratios = financial_indicators.get("Profitability Ratios", {}) or \
                        financial_indicators.get("Profitability Ratios and Growth", {})
    """ revenue_growth = profitability_ratios.get("Revenue Growth (YoY %)") or \
                     profitability_ratios.get("Revenue Growth (YoY)") or \
                     profitability_ratios.get("Revenue_Growth_YoY") or \
                     profitability_ratios.get("Revenue Growth") or \
                     profitability_ratios.get("Revenue Growth YoY") """
    revenue_growth = profitability_ratios.get("Revenue Growth")
    
    """     eps_growth = profitability_ratios.get("EPS Growth (YoY %)") or \
                 profitability_ratios.get("EPS Growth YoY") or \
                 profitability_ratios.get("EPS_Growth_YoY") or \
                 profitability_ratios.get("EPS Growth") or \
                 profitability_ratios.get("EPS Growth (YoY)") """
    eps_growth = profitability_ratios.get("EPS Growth")

    roe = profitability_ratios.get("Return on Equity (ROE)") or \
          profitability_ratios.get("ROE")

    roa = profitability_ratios.get("Return on Assets (ROA)") or \
          profitability_ratios.get("ROA")

    profit_margin = profitability_ratios.get("Profit Margin")
    operating_margin = profitability_ratios.get("Operating Margin")

    last_quarter_eps = profitability_ratios.get("Last Quarter EPS") or \
                       profitability_ratios.get("Last Quarter") or \
                       profitability_ratios.get("EPS (Last Quarter)")

    revenue_last_year = profitability_ratios.get("Revenue Last Year") or \
                        profitability_ratios.get("Revenue Last Year") 
    
    # Build growth data
    growth_data = []
    if revenue_growth != "N/A":
        growth_data.append({
            "metric": "Revenue Growth (YoY)",
            "value": revenue_growth if isinstance(revenue_growth, str) else f"{revenue_growth}%"
        })
    if eps_growth != "N/A":
        growth_data.append({
            "metric": "EPS Growth (YoY)",
            "value": eps_growth if isinstance(eps_growth, str) else f"{eps_growth}%"
        })
    """     if last_quarter_eps != "N/A":
        growth_data.append({
            "metric": "Last Quarter EPS",
            "value": f"${last_quarter_eps}" if isinstance(last_quarter_eps, (int, float)) else last_quarter_eps
        }) """
    
    return {
        # Valuation metrics
        "pe_ratio": str(pe_ratio),
        "peg_ratio": str(peg_ratio),
        "pb_ratio": str(pb_ratio),
        "ev_ebitda": "N/A",
        "debt_to_equity": str(debt_to_equity),
        
        # Profitability metrics
        "revenue_growth": str(revenue_growth),
        "eps_growth": str(eps_growth),
        "roe": str(roe),
        "roa": str(roa),
        "profit_margin": str(profit_margin),
        "operating_margin": str(operating_margin),
        
        # Price metrics
        "52_week_high": high_52w,
        "52_week_low": low_52w,
        "current_price": f"${price_movements.get('Current Price', 0)}" if price_movements.get('Current Price') else "N/A",
        
        # Risk metrics
        "beta": "N/A",
        "volatility": "N/A",
        "sharpe_ratio": "N/A",
        
        # Additional data
        "revenue_last_year": str(revenue_last_year),
        "growth_data": growth_data
    }


def extract_news_sentiment(report_data: dict) -> dict:
    """
    Extract news and sentiment data from JSON report.
    
    Args:
        report_data: Parsed JSON report data
        
    Returns:
        dict: News items and sentiment analysis
    """
    news_sentiment_data = report_data.get("News & Sentiment", {})
    recent_news = []
    if isinstance(news_sentiment_data, dict):
        news_sentiment_data = report_data.get("News & Sentiment", {})    
         # Extract recent news
        recent_news = news_sentiment_data.get("Recent News", [])    
        # Extract sentiment
        sentiment_text = news_sentiment_data.get("Sentiment", "")
    elif isinstance(news_sentiment_data, str):
        sentiment_text = news_sentiment_data    
    
    # Parse sentiment
    sentiment_score = 0.0
    sentiment_trend = "Neutral"
    
    if sentiment_text:
        sentiment_lower = sentiment_text.lower()
        
        if "cautiously optimistic" in sentiment_lower:
            sentiment_trend = "Cautiously Optimistic"
            sentiment_score = 0.5
        elif "optimistic" in sentiment_lower or "positive" in sentiment_lower or "buy" in sentiment_lower:
            sentiment_trend = "Positive"
            sentiment_score = 0.7
        elif "pessimistic" in sentiment_lower or "negative" in sentiment_lower or "sell" in sentiment_lower:
            sentiment_trend = "Negative"
            sentiment_score = -0.5
        elif "cautious" in sentiment_lower:
            sentiment_trend = "Cautious"
            sentiment_score = 0.2
        else:
            sentiment_trend = "Neutral"
            sentiment_score = 0.0
    
    # Convert news items to structured format
    news_items = []
    for i, news_text in enumerate(recent_news, 1):
        news_items.append({
            "title": f"Market Update {i}",
            "summary": news_text,
            "date": "Recent",
            "source": "Market Analysis",
            "sentiment": sentiment_trend
        })
    
    # Extract analyst ratings from sentiment text
    analyst_ratings = {
        "consensus": "N/A",
        "buy": "N/A",
        "hold": "N/A",
        "sell": "N/A",
        "avg_target": "N/A"
    }
    
    if "buy" in sentiment_text.lower():
        analyst_ratings["consensus"] = "Buy"
    elif "hold" in sentiment_text.lower():
        analyst_ratings["consensus"] = "Hold"
    elif "sell" in sentiment_text.lower():
        analyst_ratings["consensus"] = "Sell"
    
    return {
        "sentiment_score": round(sentiment_score, 2),
        "sentiment_trend": sentiment_trend,
        "news_count": len(news_items),
        "social_mentions": "N/A",
        "news_items": news_items,
        "analyst_ratings": analyst_ratings,
        "summary": sentiment_text
    }


def extract_risks_opportunities(report_data: dict) -> dict:
    """
    Extract risks and opportunities from JSON report.
    
    Args:
        report_data: Parsed JSON report data
        
    Returns:
        dict: Risks, opportunities, and SWOT analysis
    """
    
    risks_opps_data = report_data.get("Risks & Opportunities", {})
    
    # Extract opportunities
    opportunities_list = risks_opps_data.get("Opportunities", [])
    opportunities = []
    
    for opp_text in opportunities_list:
        # Try to split title and description
        if '.' in opp_text:
            parts = opp_text.split('.', 1)
            title = parts[0].strip()
            description = parts[1].strip() if len(parts) > 1 else opp_text
        else:
            title = opp_text[:50] + "..." if len(opp_text) > 50 else opp_text
            description = opp_text
        
        opportunities.append({
            "title": title,
            "description": description,
            "impact": "High",
            "probability": "Medium"
        })
    
    # Extract risks
    risks_list = risks_opps_data.get("Risks", [])
    risks = []
    
    for risk_text in risks_list:
        # Try to split title and description
        if '.' in risk_text:
            parts = risk_text.split('.', 1)
            title = parts[0].strip()
            description = parts[1].strip() if len(parts) > 1 else risk_text
        else:
            title = risk_text[:50] + "..." if len(risk_text) > 50 else risk_text
            description = risk_text
        
        risks.append({
            "title": title,
            "description": description,
            "impact": "Medium",
            "probability": "Medium"
        })
    
    # Build SWOT analysis
    swot = build_swot_from_report(report_data, opportunities_list, risks_list)
    
    return {
        "opportunities": opportunities,
        "risks": risks,
        "swot": swot
    }


def determine_recommendation(exec_summary: str, report_data: dict) -> str:
    """
    Determine investment recommendation from report data.
    
    Args:
        exec_summary: Executive summary text
        report_data: Full report data
        
    Returns:
        str: Investment recommendation (Buy, Hold, Sell)
    """
    
    text_lower = exec_summary.lower()
    
    # Check sentiment
    news_sentiment = report_data.get("News & Sentiment", {})
    if isinstance(news_sentiment, dict):
        sentiment_text = news_sentiment.get("Sentiment", "").lower()
    elif isinstance(news_sentiment, str):
        sentiment_text = news_sentiment
    else:
        sentiment_text = "N/A"
    
    # Strong buy signals
    if "strong buy" in text_lower or "strong buy" in sentiment_text:
        return "Strong Buy"
    
    # Buy signals
    if "buy" in sentiment_text or "bullish" in text_lower or "attractive investment" in text_lower:
        return "Buy"
    
    # Sell signals
    if "sell" in sentiment_text or "bearish" in text_lower or "avoid" in text_lower:
        return "Sell"
    
    # Hold/Neutral signals
    if "neutral" in text_lower or "hold" in sentiment_text or "balanced" in text_lower:
        return "Hold"
    
    # Default to neutral
    return "Neutral"


def assess_risk_level(report_data: dict) -> str:
    """
    Assess overall risk level from report.
    
    Args:
        report_data: Full report data
        
    Returns:
        str: Risk level (Low, Medium, High)
    """
    
    risks_data = report_data.get("Risks & Opportunities", {})
    risks_list = risks_data.get("Risks", [])
    
    # Count risk items
    risk_count = len(risks_list)
    
    # Check for high-severity keywords
    high_severity_keywords = ['significant', 'major', 'severe', 'critical', 'substantial']
    
    high_severity_count = 0
    for risk in risks_list:
        risk_lower = risk.lower()
        if any(keyword in risk_lower for keyword in high_severity_keywords):
            high_severity_count += 1
    
    # Determine risk level
    if risk_count >= 5 or high_severity_count >= 2:
        return "High"
    elif risk_count <= 2 and high_severity_count == 0:
        return "Low"
    else:
        return "Medium"


def extract_market_cap(report_data: dict) -> str:
    """
    Extract market capitalization from report.
    
    Args:
        report_data: Full report data
        
    Returns:
        str: Market cap formatted string
    """
    
    full_report = report_data.get("Full Report", "")
    
    # Try to find market cap in full report
    market_cap_match = re.search(
        r'Market\s+Cap(?:italization)?[:\s]+(?:Approx\.\s+)?\$?([\d.]+\s*(?:Trillion|Billion|Million))',
        full_report,
        re.IGNORECASE
    )
    
    if market_cap_match:
        return f"${market_cap_match.group(1)}"
    
    return "N/A"


def build_swot_from_report(report_data: dict, opportunities_list: List[str], risks_list: List[str]) -> dict:
    """
    Build SWOT analysis from report data.
    
    Args:
        report_data: Full report data
        opportunities_list: List of opportunity texts
        risks_list: List of risk texts
        
    Returns:
        dict: SWOT analysis with strengths, weaknesses, opportunities, threats
    """
    
    exec_summary = report_data.get("Executive Summary", "").lower()
    full_report = report_data.get("Full Report", "").lower()
    
    # Strengths - look for positive indicators
    strengths = []
    
    strength_indicators = [
        ("market leader", "Market leadership position"),
        ("strong brand", "Strong brand recognition and loyalty"),
        ("innovation", "Innovation capabilities"),
        ("ecosystem", "Integrated product ecosystem"),
        ("revenue growth", "Strong revenue growth"),
        ("profitability", "Solid profitability metrics"),
        ("customer loyalty", "High customer loyalty")
    ]
    
    for indicator, strength_text in strength_indicators:
        if indicator in exec_summary or indicator in full_report:
            strengths.append(strength_text)
    
    # Limit to top 5 strengths
    strengths = strengths[:5] if strengths else ["Strong financial position", "Market presence"]
    
    # Weaknesses - extract from risks or look for negative indicators
    weaknesses = []
    
    weakness_indicators = [
        "regulatory scrutiny",
        "high valuation",
        "supply chain",
        "competition",
        "premium pricing"
    ]
    
    for indicator in weakness_indicators:
        if indicator in exec_summary or indicator in full_report:
            weaknesses.append(indicator.title())
    
    weaknesses = weaknesses[:4] if weaknesses else ["Regulatory challenges", "Market competition"]
    
    # Opportunities - extract titles from opportunities list
    opportunities = []
    for opp in opportunities_list[:5]:
        # Extract first sentence or first 60 characters
        opp_title = opp.split('.')[0] if '.' in opp else opp[:60]
        opportunities.append(opp_title.strip())
    
    if not opportunities:
        opportunities = ["Market expansion", "New product launches"]
    
    # Threats - extract from risks list
    threats = []
    for risk in risks_list[:5]:
        # Extract first sentence or first 60 characters
        risk_title = risk.split('.')[0] if '.' in risk else risk[:60]
        threats.append(risk_title.strip())
    
    if not threats:
        threats = ["Economic uncertainty", "Competitive pressures"]
    
    return {
        "strengths": strengths,
        "weaknesses": weaknesses,
        "opportunities": opportunities,
        "threats": threats
    }