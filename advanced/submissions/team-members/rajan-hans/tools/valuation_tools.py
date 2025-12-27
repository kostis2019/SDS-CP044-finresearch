# tools/valuation_tools.py
# Enhanced valuation metrics: EV/EBITDA, FCF Yield, Price/Sales, etc.
# Phase 1 Enhancement
# ---------------------------------------------

from typing import Dict, Any, Optional

from tools.yfinance_provider import get_yfinance_provider


def get_valuation_metrics(ticker: str) -> Dict[str, Any]:
    """
    Fetch comprehensive valuation metrics for a stock.
    
    Parameters
    ----------
    ticker : str
        Stock ticker symbol
    
    Returns
    -------
    dict
        {
            "status": "success" | "partial" | "error",
            "ticker": str,
            "current_price": float,
            "market_cap": float,
            "enterprise_value": float,
            
            # Traditional Ratios
            "pe_ttm": float,
            "pe_forward": float,
            "peg_ratio": float,
            "price_to_book": float,
            "price_to_sales": float,
            
            # Enterprise Value Ratios (NEW)
            "ev_to_ebitda": float,
            "ev_to_revenue": float,
            "ev_to_fcf": float,
            
            # Cash Flow Based (NEW)
            "fcf_yield": float,
            "fcf_per_share": float,
            "price_to_fcf": float,
            "earnings_yield": float,
            
            # Dividend
            "dividend_yield": float,
            "payout_ratio": float,
            
            # Valuation Assessment
            "valuation_label": "Undervalued" | "Fair Value" | "Overvalued",
            "valuation_score": float (0-100)
        }
    """
    try:
        provider = get_yfinance_provider()
        info = provider.get_info(ticker)
        
        # Basic price and market data
        current_price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
        market_cap = info.get('marketCap', 0)
        enterprise_value = info.get('enterpriseValue', 0)
        shares_outstanding = info.get('sharesOutstanding', 0)
        
        # Traditional ratios
        pe_ttm = info.get('trailingPE')
        pe_forward = info.get('forwardPE')
        peg_ratio = info.get('pegRatio')
        price_to_book = info.get('priceToBook')
        price_to_sales = info.get('priceToSalesTrailing12Months')
        
        # Enterprise Value ratios
        ev_to_ebitda = info.get('enterpriseToEbitda')
        ev_to_revenue = info.get('enterpriseToRevenue')
        
        # Free Cash Flow metrics
        free_cash_flow = info.get('freeCashflow', 0)
        operating_cash_flow = info.get('operatingCashflow', 0)
        
        # Calculate FCF Yield (FCF / Market Cap)
        fcf_yield = None
        if free_cash_flow and market_cap and market_cap > 0:
            fcf_yield = (free_cash_flow / market_cap) * 100
        
        # Calculate FCF per share
        fcf_per_share = None
        if free_cash_flow and shares_outstanding and shares_outstanding > 0:
            fcf_per_share = free_cash_flow / shares_outstanding
        
        # Calculate Price to FCF
        price_to_fcf = None
        if fcf_per_share and fcf_per_share > 0 and current_price:
            price_to_fcf = current_price / fcf_per_share
        
        # Calculate EV/FCF
        ev_to_fcf = None
        if enterprise_value and free_cash_flow and free_cash_flow > 0:
            ev_to_fcf = enterprise_value / free_cash_flow
        
        # Earnings Yield (inverse of P/E)
        earnings_yield = None
        if pe_ttm and pe_ttm > 0:
            earnings_yield = (1 / pe_ttm) * 100
        
        # Dividend metrics
        dividend_yield = info.get('dividendYield')
        if dividend_yield:
            dividend_yield = dividend_yield * 100
        payout_ratio = info.get('payoutRatio')
        if payout_ratio:
            payout_ratio = payout_ratio * 100
        
        # Calculate valuation score and label
        valuation_score, valuation_label = _calculate_valuation_assessment(
            pe_ttm=pe_ttm,
            pe_forward=pe_forward,
            peg_ratio=peg_ratio,
            price_to_book=price_to_book,
            ev_to_ebitda=ev_to_ebitda,
            fcf_yield=fcf_yield,
            price_to_fcf=price_to_fcf
        )
        
        # Determine status
        has_data = any([pe_ttm, pe_forward, ev_to_ebitda, fcf_yield])
        status = "success" if has_data else "partial"
        
        return {
            "status": status,
            "ticker": ticker,
            "current_price": _safe_round(current_price, 2),
            "market_cap": market_cap,
            "enterprise_value": enterprise_value,
            
            # Traditional Ratios
            "pe_ttm": _safe_round(pe_ttm, 2),
            "pe_forward": _safe_round(pe_forward, 2),
            "peg_ratio": _safe_round(peg_ratio, 2),
            "price_to_book": _safe_round(price_to_book, 2),
            "price_to_sales": _safe_round(price_to_sales, 2),
            
            # Enterprise Value Ratios
            "ev_to_ebitda": _safe_round(ev_to_ebitda, 2),
            "ev_to_revenue": _safe_round(ev_to_revenue, 2),
            "ev_to_fcf": _safe_round(ev_to_fcf, 2),
            
            # Cash Flow Based
            "free_cash_flow": free_cash_flow,
            "fcf_yield": _safe_round(fcf_yield, 2),
            "fcf_per_share": _safe_round(fcf_per_share, 2),
            "price_to_fcf": _safe_round(price_to_fcf, 2),
            "earnings_yield": _safe_round(earnings_yield, 2),
            
            # Dividend
            "dividend_yield": _safe_round(dividend_yield, 2),
            "payout_ratio": _safe_round(payout_ratio, 2),
            
            # Assessment
            "valuation_label": valuation_label,
            "valuation_score": valuation_score
        }
        
    except Exception as e:
        return {
            "status": "error",
            "ticker": ticker,
            "error": str(e),
            "valuation_label": "Unknown",
            "valuation_score": 50
        }


def _safe_round(value: Optional[float], decimals: int = 2) -> Optional[float]:
    """Safely round a value, returning None if input is None."""
    if value is None:
        return None
    try:
        return round(float(value), decimals)
    except (TypeError, ValueError):
        return None


def _calculate_valuation_assessment(
    pe_ttm: Optional[float],
    pe_forward: Optional[float],
    peg_ratio: Optional[float],
    price_to_book: Optional[float],
    ev_to_ebitda: Optional[float],
    fcf_yield: Optional[float],
    price_to_fcf: Optional[float]
) -> tuple:
    """
    Calculate a valuation score and label based on multiple metrics.
    
    Returns
    -------
    tuple
        (valuation_score, valuation_label)
    """
    scores = []
    
    # P/E TTM scoring (lower is better, but not negative)
    if pe_ttm and pe_ttm > 0:
        if pe_ttm < 10:
            scores.append(90)
        elif pe_ttm < 15:
            scores.append(75)
        elif pe_ttm < 20:
            scores.append(60)
        elif pe_ttm < 25:
            scores.append(50)
        elif pe_ttm < 35:
            scores.append(35)
        else:
            scores.append(20)
    
    # Forward P/E scoring
    if pe_forward and pe_forward > 0:
        if pe_forward < 12:
            scores.append(85)
        elif pe_forward < 18:
            scores.append(70)
        elif pe_forward < 25:
            scores.append(50)
        else:
            scores.append(30)
    
    # PEG Ratio scoring (1 is fair value)
    if peg_ratio and peg_ratio > 0:
        if peg_ratio < 0.5:
            scores.append(95)
        elif peg_ratio < 1.0:
            scores.append(80)
        elif peg_ratio < 1.5:
            scores.append(60)
        elif peg_ratio < 2.0:
            scores.append(40)
        else:
            scores.append(20)
    
    # EV/EBITDA scoring
    if ev_to_ebitda and ev_to_ebitda > 0:
        if ev_to_ebitda < 8:
            scores.append(85)
        elif ev_to_ebitda < 12:
            scores.append(70)
        elif ev_to_ebitda < 16:
            scores.append(55)
        elif ev_to_ebitda < 20:
            scores.append(40)
        else:
            scores.append(25)
    
    # FCF Yield scoring (higher is better)
    if fcf_yield:
        if fcf_yield > 8:
            scores.append(90)
        elif fcf_yield > 5:
            scores.append(75)
        elif fcf_yield > 3:
            scores.append(60)
        elif fcf_yield > 1:
            scores.append(45)
        elif fcf_yield > 0:
            scores.append(35)
        else:
            scores.append(20)  # Negative FCF
    
    # Price to Book scoring
    if price_to_book and price_to_book > 0:
        if price_to_book < 1:
            scores.append(90)
        elif price_to_book < 2:
            scores.append(70)
        elif price_to_book < 4:
            scores.append(50)
        else:
            scores.append(30)
    
    # Calculate average score
    if scores:
        valuation_score = round(sum(scores) / len(scores), 1)
    else:
        valuation_score = 50  # Default to neutral
    
    # Determine label
    if valuation_score >= 70:
        valuation_label = "Undervalued"
    elif valuation_score >= 45:
        valuation_label = "Fair Value"
    else:
        valuation_label = "Overvalued"
    
    return valuation_score, valuation_label


def compare_valuation_to_sector(
    ticker: str, 
    sector_pe_median: float = 20,
    sector_ev_ebitda_median: float = 12,
    sector_ps_median: float = 2
) -> Dict[str, Any]:
    """
    Compare a stock's valuation to sector medians.
    
    Parameters
    ----------
    ticker : str
        Stock ticker symbol
    sector_pe_median : float
        Sector median P/E ratio
    sector_ev_ebitda_median : float
        Sector median EV/EBITDA
    sector_ps_median : float
        Sector median Price/Sales
    
    Returns
    -------
    dict
        Comparison metrics with premium/discount percentages
    """
    metrics = get_valuation_metrics(ticker)
    
    comparisons = {}
    
    # P/E comparison
    if metrics.get('pe_ttm'):
        pe_premium = ((metrics['pe_ttm'] / sector_pe_median) - 1) * 100
        comparisons['pe_vs_sector'] = {
            'stock_pe': metrics['pe_ttm'],
            'sector_median': sector_pe_median,
            'premium_percent': round(pe_premium, 1),
            'assessment': 'Premium' if pe_premium > 10 else 'Discount' if pe_premium < -10 else 'In-line'
        }
    
    # EV/EBITDA comparison
    if metrics.get('ev_to_ebitda'):
        ev_premium = ((metrics['ev_to_ebitda'] / sector_ev_ebitda_median) - 1) * 100
        comparisons['ev_ebitda_vs_sector'] = {
            'stock_ev_ebitda': metrics['ev_to_ebitda'],
            'sector_median': sector_ev_ebitda_median,
            'premium_percent': round(ev_premium, 1),
            'assessment': 'Premium' if ev_premium > 10 else 'Discount' if ev_premium < -10 else 'In-line'
        }
    
    # P/S comparison
    if metrics.get('price_to_sales'):
        ps_premium = ((metrics['price_to_sales'] / sector_ps_median) - 1) * 100
        comparisons['ps_vs_sector'] = {
            'stock_ps': metrics['price_to_sales'],
            'sector_median': sector_ps_median,
            'premium_percent': round(ps_premium, 1),
            'assessment': 'Premium' if ps_premium > 10 else 'Discount' if ps_premium < -10 else 'In-line'
        }
    
    return {
        "ticker": ticker,
        "valuation_metrics": metrics,
        "sector_comparisons": comparisons
    }
