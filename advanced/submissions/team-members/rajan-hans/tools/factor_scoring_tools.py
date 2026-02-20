# tools/factor_scoring_tools.py
# Compute factor scores based on fundamental and technical metrics
# ---------------------------------------------


def _clamp(value, min_val=0.0, max_val=100.0):
    """Clamp a value between min and max."""
    if value is None:
        return (min_val + max_val) / 2  # Return midpoint for None
    return max(min_val, min(max_val, value))


def _score_valuation(fundamentals: dict, benchmarks: dict = None) -> float:
    """
    Score valuation based on PE ratios relative to sector benchmarks.
    
    Scoring logic:
    - PE significantly below sector: High score (undervalued)
    - PE near sector median: Medium score (fair value)
    - PE significantly above sector: Low score (overvalued)
    
    Also considers PEG ratio if available.
    """
    # Try to get PE values from different possible locations
    pe_ttm = (
        fundamentals.get("pe_ttm") or 
        fundamentals.get("pe") or 
        fundamentals.get("trailing_pe")
    )
    forward_pe = (
        fundamentals.get("forward_pe") or 
        fundamentals.get("pe_forward")
    )
    peg_ratio = fundamentals.get("peg_ratio")
    
    # Get sector benchmarks
    sector_pe = None
    if benchmarks:
        sector_pe = (
            benchmarks.get("sector_pe_median") or 
            benchmarks.get("sector_pe") or
            benchmarks.get("pe_median")
        )
    
    # Use forward PE if available (more forward-looking), else trailing
    pe_to_use = forward_pe or pe_ttm
    
    if pe_to_use is None:
        return 50.0  # Neutral if no PE data
    
    # Handle negative PE (unprofitable companies)
    if pe_to_use <= 0:
        return 25.0  # Low score for unprofitable
    
    score = 50.0  # Start neutral
    
    # Score based on absolute PE ranges
    if pe_to_use < 10:
        score = 85.0  # Very cheap
    elif pe_to_use < 15:
        score = 75.0  # Cheap
    elif pe_to_use < 20:
        score = 65.0  # Reasonable
    elif pe_to_use < 25:
        score = 55.0  # Slightly expensive
    elif pe_to_use < 35:
        score = 40.0  # Expensive
    else:
        score = 25.0  # Very expensive
    
    # Adjust based on sector comparison if available
    if sector_pe and sector_pe > 0:
        pe_ratio = pe_to_use / sector_pe
        
        if pe_ratio < 0.7:
            score += 15  # Significantly below sector
        elif pe_ratio < 0.9:
            score += 8   # Below sector
        elif pe_ratio > 1.3:
            score -= 15  # Significantly above sector
        elif pe_ratio > 1.1:
            score -= 8   # Above sector
    
    # Adjust based on PEG ratio if available (PE relative to growth)
    if peg_ratio is not None and peg_ratio > 0:
        if peg_ratio < 1.0:
            score += 10  # Good value relative to growth
        elif peg_ratio < 1.5:
            score += 5
        elif peg_ratio > 2.5:
            score -= 10  # Expensive relative to growth
        elif peg_ratio > 2.0:
            score -= 5
    
    return _clamp(score)


def _score_growth(growth: dict) -> float:
    """Score growth based on revenue and EPS CAGRs."""
    rev_cagr = growth.get("revenue_cagr_3y")
    eps_cagr = growth.get("eps_cagr_3y")
    revenue_yoy = growth.get("revenue_yoy")

    def cagr_score(cagr, is_eps=False):
        if cagr is None:
            return 50
        if is_eps:
            if cagr >= 0.25:
                return 95
            if cagr >= 0.15:
                return 80
            if cagr >= 0.08:
                return 65
            if cagr >= 0.00:
                return 45
            return 20
        else:
            if cagr >= 0.20:
                return 95
            if cagr >= 0.12:
                return 80
            if cagr >= 0.06:
                return 65
            if cagr >= 0.00:
                return 45
            return 25

    score = (cagr_score(rev_cagr) + cagr_score(eps_cagr, True)) / 2

    # Bonus/penalty for acceleration/deceleration
    if revenue_yoy is not None:
        if revenue_yoy > (rev_cagr or 0):
            score += 5  # Accelerating growth
        elif revenue_yoy < (rev_cagr or 0):
            score -= 5  # Decelerating growth

    return _clamp(score)


def _score_profitability(profit: dict) -> float:
    """Score profitability based on ROE and operating margin."""
    roe = profit.get("roe")
    op_margin = profit.get("operating_margin")

    def roe_score(val):
        if val is None:
            return 50
        if val >= 0.25:
            return 95
        if val >= 0.15:
            return 80
        if val >= 0.10:
            return 65
        if val >= 0.05:
            return 45
        return 25

    def margin_score(val):
        if val is None:
            return 50
        if val >= 0.30:
            return 95
        if val >= 0.20:
            return 80
        if val >= 0.10:
            return 60
        if val >= 0.00:
            return 40
        return 20

    return _clamp((roe_score(roe) + margin_score(op_margin)) / 2)


def _score_financial_health(health: dict) -> float:
    """Score financial health based on debt/equity and interest coverage."""
    debt_equity = health.get("debt_equity")
    interest_coverage = health.get("interest_coverage")

    def de_score(val):
        if val is None:
            return 50
        if val <= 0.3:
            return 95
        if val <= 0.6:
            return 80
        if val <= 1.0:
            return 60
        if val <= 2.0:
            return 40
        return 20

    def ic_score(val):
        if val is None:
            return 50
        if val >= 10:
            return 95
        if val >= 6:
            return 80
        if val >= 3:
            return 60
        if val >= 1:
            return 35
        return 15

    return _clamp((de_score(debt_equity) + ic_score(interest_coverage)) / 2)


def _score_technicals(tech: dict) -> float:
    """Score technical indicators based on RSI, trend, and drawdown."""
    rsi = tech.get("rsi14") or tech.get("rsi_14") or tech.get("rsi")
    trend = tech.get("trend_label") or tech.get("trend")
    drawdown = tech.get("max_drawdown_1y") or tech.get("max_drawdown")

    def rsi_score(val):
        if val is None:
            return 50
        if 40 <= val <= 60:
            return 80  # Neutral zone - healthy
        if 60 < val <= 70:
            return 70  # Slightly overbought
        if 30 <= val < 40:
            return 55  # Slightly oversold (potential opportunity)
        if val > 70:
            return 40  # Overbought - caution
        return 35  # Oversold - could be distressed

    def trend_score(label):
        if label is None:
            return 50
        label_lower = str(label).lower()
        if label_lower == "uptrend":
            return 85
        if label_lower == "sideways":
            return 55
        if label_lower == "downtrend":
            return 25
        return 50

    def dd_score(val):
        if val is None:
            return 50
        val = abs(val)
        if val < 0.10:
            return 90  # Low drawdown
        if val < 0.20:
            return 70
        if val < 0.35:
            return 45
        return 25  # High drawdown - risky

    return _clamp((rsi_score(rsi) + trend_score(trend) + dd_score(drawdown)) / 3)


def compute_factor_scores(
    fundamental_metrics: dict,
    technical_indicators: dict,
    sector_benchmarks: dict = None,
    sentiment_adjustment: float = 0.0,
) -> dict:
    """
    Compute all factor scores and final rating using deterministic rules.
    
    Parameters
    ----------
    fundamental_metrics : dict
        Dict containing growth, profitability, financial_health sub-dicts
    technical_indicators : dict
        Dict containing rsi14, trend_label, max_drawdown_1y, etc.
    sector_benchmarks : dict, optional
        Dict containing sector median values for comparison
    sentiment_adjustment : float
        Adjustment from -5 to +5 based on news sentiment
    
    Returns
    -------
    dict
        All factor scores and final rating
    """
    # Extract valuation data from fundamentals for valuation scoring
    valuation_data = {
        "pe_ttm": fundamental_metrics.get("pe_ttm"),
        "forward_pe": fundamental_metrics.get("forward_pe"),
        "peg_ratio": fundamental_metrics.get("peg_ratio"),
    }
    
    # Also check if these are nested in a "valuation" key
    if "valuation" in fundamental_metrics:
        valuation_data.update(fundamental_metrics["valuation"])
    
    # Compute individual factor scores
    valuation_score = _score_valuation(valuation_data, sector_benchmarks)
    growth_score = _score_growth(fundamental_metrics.get("growth", {}))
    profitability_score = _score_profitability(fundamental_metrics.get("profitability", {}))
    financial_health_score = _score_financial_health(fundamental_metrics.get("financial_health", {}))
    technical_score = _score_technicals(technical_indicators)

    # Compute composite score with weights
    # Valuation: 25%, Growth: 25%, Profitability: 15%, Health: 15%, Technical: 20%
    composite_score = (
        0.25 * valuation_score
        + 0.25 * growth_score
        + 0.15 * profitability_score
        + 0.15 * financial_health_score
        + 0.20 * technical_score
    )

    # Apply sentiment adjustment (clamped to -5 to +5)
    sentiment_adjustment = max(-5.0, min(5.0, sentiment_adjustment))
    final_score = _clamp(composite_score + sentiment_adjustment)

    # Determine rating based on final score
    if final_score >= 80:
        rating = "STRONG BUY"
    elif final_score >= 65:
        rating = "BUY"
    elif final_score >= 45:
        rating = "HOLD"
    elif final_score >= 30:
        rating = "REDUCE"
    else:
        rating = "SELL"

    return {
        "valuation_score": round(valuation_score, 2),
        "growth_score": round(growth_score, 2),
        "profitability_score": round(profitability_score, 2),
        "financial_health_score": round(financial_health_score, 2),
        "technical_score": round(technical_score, 2),
        "composite_score": round(composite_score, 2),
        "sentiment_adjustment": round(sentiment_adjustment, 2),
        "final_score": round(final_score, 2),
        "rating": rating,
    }
