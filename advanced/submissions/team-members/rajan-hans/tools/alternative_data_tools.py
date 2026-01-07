# tools/alternative_data_tools.py
# Fetch alternative data: Insider Transactions, Analyst Recommendations, Institutional Holders
# ---------------------------------------------

import pandas as pd
from typing import Dict, Any, List
from datetime import datetime, timedelta

from tools.yfinance_provider import get_yfinance_provider


def get_insider_transactions(ticker: str, days_back: int = 90) -> Dict[str, Any]:
    """
    Fetch recent insider transactions for a stock.
    
    Parameters
    ----------
    ticker : str
        Stock ticker symbol
    days_back : int
        Number of days to look back for transactions (default 90)
    
    Returns
    -------
    dict
        Insider transaction data with summary statistics
    """
    try:
        provider = get_yfinance_provider()
        
        # Get insider transactions from cached provider
        insider_df = provider.get_insider_transactions(ticker)
        
        if insider_df is None or insider_df.empty:
            return {
                "status": "no_data",
                "ticker": ticker,
                "transactions": [],
                "summary": {
                    "total_buys": 0,
                    "total_sells": 0,
                    "net_shares": 0,
                    "net_value": 0,
                    "buy_sell_ratio": 1.0,  # Neutral
                    "insider_sentiment": "Neutral"
                },
                "message": "No insider transaction data available"
            }
        
        transactions = []
        total_buys = 0
        total_sells = 0
        buy_value = 0
        sell_value = 0
        
        for idx, row in insider_df.iterrows():
            # Parse transaction date
            trans_date = None
            if 'Start Date' in insider_df.columns:
                trans_date = row.get('Start Date')
            elif 'Date' in insider_df.columns:
                trans_date = row.get('Date')
            
            # Determine transaction type
            trans_text = str(row.get('Text', '')).lower()
            shares = row.get('Shares', 0) or 0
            value = row.get('Value', 0) or 0
            
            if 'purchase' in trans_text or 'buy' in trans_text or 'acquisition' in trans_text:
                trans_type = "Buy"
                total_buys += 1
                buy_value += abs(value)
            elif 'sale' in trans_text or 'sell' in trans_text or 'disposition' in trans_text:
                trans_type = "Sell"
                total_sells += 1
                sell_value += abs(value)
            else:
                trans_type = "Other"
            
            transactions.append({
                "insider_name": row.get('Insider', 'Unknown'),
                "title": row.get('Position', 'Unknown'),
                "transaction_type": trans_type,
                "shares": int(shares) if pd.notna(shares) else 0,
                "value": float(value) if pd.notna(value) else 0,
                "date": str(trans_date) if trans_date else "Unknown",
                "text": row.get('Text', '')
            })
        
        # Calculate summary metrics
        net_value = buy_value - sell_value
        
        # Calculate buy/sell ratio safely (avoid infinity)
        if total_sells > 0:
            buy_sell_ratio = total_buys / total_sells
        elif total_buys > 0:
            buy_sell_ratio = 10.0  # High but finite value indicating strong buying
        else:
            buy_sell_ratio = 1.0  # Neutral when no transactions
        
        # Cap the ratio at a reasonable maximum
        buy_sell_ratio = min(buy_sell_ratio, 99.0)
        
        # Determine insider sentiment
        if buy_sell_ratio > 1.5 or (total_buys > 0 and total_sells == 0):
            insider_sentiment = "Bullish"
        elif buy_sell_ratio < 0.5 or (total_sells > 0 and total_buys == 0):
            insider_sentiment = "Bearish"
        else:
            insider_sentiment = "Neutral"
        
        return {
            "status": "success",
            "ticker": ticker,
            "transactions": transactions[:10],  # Limit to 10 most recent
            "summary": {
                "total_buys": total_buys,
                "total_sells": total_sells,
                "net_value": round(net_value, 2),
                "buy_sell_ratio": round(buy_sell_ratio, 2),
                "insider_sentiment": insider_sentiment
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "ticker": ticker,
            "transactions": [],
            "summary": {
                "total_buys": 0,
                "total_sells": 0,
                "net_value": 0,
                "buy_sell_ratio": 1.0,
                "insider_sentiment": "Neutral"
            },
            "error": str(e)
        }


def get_analyst_recommendations(ticker: str) -> Dict[str, Any]:
    """
    Fetch analyst recommendations and price targets.
    
    Parameters
    ----------
    ticker : str
        Stock ticker symbol
    
    Returns
    -------
    dict
        Analyst recommendations, price targets, and consensus rating
    """
    try:
        provider = get_yfinance_provider()
        info = provider.get_info(ticker)
        
        # Get current price
        current_price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
        
        # Get price targets
        target_low = info.get('targetLowPrice')
        target_mean = info.get('targetMeanPrice')
        target_median = info.get('targetMedianPrice')
        target_high = info.get('targetHighPrice')
        
        # Calculate upside
        upside_percent = 0
        if target_mean and current_price:
            upside_percent = ((target_mean - current_price) / current_price) * 100
        
        # Get recommendation counts from cached provider
        recommendations = provider.get_recommendations(ticker)
        
        rec_counts = {
            "strong_buy": 0,
            "buy": 0,
            "hold": 0,
            "sell": 0,
            "strong_sell": 0
        }
        
        recent_changes = []
        
        if recommendations is not None and not recommendations.empty:
            # Get the most recent recommendations (last 3 months)
            recent_recs = recommendations.tail(20)
            
            for idx, row in recent_recs.iterrows():
                grade = str(row.get('To Grade', '')).lower()
                
                if 'strong buy' in grade or 'strongbuy' in grade:
                    rec_counts["strong_buy"] += 1
                elif 'buy' in grade or 'outperform' in grade or 'overweight' in grade:
                    rec_counts["buy"] += 1
                elif 'hold' in grade or 'neutral' in grade or 'equal' in grade or 'market perform' in grade:
                    rec_counts["hold"] += 1
                elif 'strong sell' in grade or 'strongsell' in grade:
                    rec_counts["strong_sell"] += 1
                elif 'sell' in grade or 'underperform' in grade or 'underweight' in grade:
                    rec_counts["sell"] += 1
                
                recent_changes.append({
                    "firm": row.get('Firm', 'Unknown'),
                    "to_grade": row.get('To Grade', 'Unknown'),
                    "from_grade": row.get('From Grade', ''),
                    "action": row.get('Action', ''),
                    "date": str(idx) if idx else "Unknown"
                })
        
        # Also check recommendationKey from info
        rec_key = info.get('recommendationKey', '')
        
        # Determine consensus
        total = sum(rec_counts.values())
        if total > 0:
            bullish = rec_counts["strong_buy"] + rec_counts["buy"]
            bearish = rec_counts["sell"] + rec_counts["strong_sell"]
            
            if rec_counts["strong_buy"] > total * 0.4:
                consensus = "Strong Buy"
            elif bullish > total * 0.6:
                consensus = "Buy"
            elif bearish > total * 0.4:
                consensus = "Sell"
            elif rec_counts["strong_sell"] > total * 0.2:
                consensus = "Strong Sell"
            else:
                consensus = "Hold"
        else:
            # Use recommendationKey from info as fallback
            if rec_key:
                consensus = rec_key.replace('_', ' ').title()
            else:
                consensus = "No Data"
        
        # Get number of analysts
        num_analysts = info.get('numberOfAnalystOpinions', total)
        
        return {
            "status": "success" if (target_mean or total > 0) else "no_data",
            "ticker": ticker,
            "current_price": round(current_price, 2) if current_price else None,
            "target_prices": {
                "low": round(target_low, 2) if target_low else None,
                "mean": round(target_mean, 2) if target_mean else None,
                "median": round(target_median, 2) if target_median else None,
                "high": round(target_high, 2) if target_high else None
            },
            "upside_percent": round(upside_percent, 2),
            "recommendations": rec_counts,
            "consensus": consensus,
            "total_analysts": num_analysts,
            "recent_changes": recent_changes[:5]  # Last 5 changes
        }
        
    except Exception as e:
        return {
            "status": "error",
            "ticker": ticker,
            "current_price": None,
            "target_prices": {},
            "upside_percent": 0,
            "recommendations": {},
            "consensus": "Error",
            "total_analysts": 0,
            "error": str(e)
        }


def get_institutional_holders(ticker: str) -> Dict[str, Any]:
    """
    Fetch institutional ownership data.
    
    Parameters
    ----------
    ticker : str
        Stock ticker symbol
    
    Returns
    -------
    dict
        Institutional ownership data with top holders
    """
    try:
        provider = get_yfinance_provider()
        info = provider.get_info(ticker)
        
        # Get institutional ownership percentage
        inst_ownership = info.get('heldPercentInstitutions', 0)
        if inst_ownership:
            inst_ownership = round(inst_ownership * 100, 2)
        
        # Get institutional holders from cached provider
        inst_holders = provider.get_institutional_holders(ticker)
        
        top_holders = []
        total_shares = 0
        
        if inst_holders is not None and not inst_holders.empty:
            for idx, row in inst_holders.head(10).iterrows():
                shares = row.get('Shares', 0) or 0
                total_shares += shares
                
                top_holders.append({
                    "holder": row.get('Holder', 'Unknown'),
                    "shares": int(shares),
                    "value": float(row.get('Value', 0) or 0),
                    "percent_held": float(row.get('% Out', 0) or 0),
                    "date_reported": str(row.get('Date Reported', ''))
                })
        
        # Determine concentration
        if len(top_holders) > 0:
            top_5_percent = sum(h['percent_held'] for h in top_holders[:5])
            if top_5_percent > 30:
                concentration = "High"
            elif top_5_percent > 15:
                concentration = "Medium"
            else:
                concentration = "Low"
        else:
            concentration = "Unknown"
        
        return {
            "status": "success" if top_holders else "no_data",
            "ticker": ticker,
            "institutional_ownership_percent": inst_ownership,
            "top_holders": top_holders,
            "summary": {
                "total_institutional_shares": int(total_shares),
                "num_institutions": len(top_holders),
                "concentration": concentration
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "ticker": ticker,
            "institutional_ownership_percent": 0,
            "top_holders": [],
            "summary": {
                "total_institutional_shares": 0,
                "num_institutions": 0,
                "concentration": "Unknown"
            },
            "error": str(e)
        }


def get_all_alternative_data(ticker: str) -> Dict[str, Any]:
    """
    Fetch all alternative data for a stock in one call.
    
    Parameters
    ----------
    ticker : str
        Stock ticker symbol
    
    Returns
    -------
    dict
        Combined output from all alternative data functions
    """
    return {
        "ticker": ticker,
        "insider_transactions": get_insider_transactions(ticker),
        "analyst_recommendations": get_analyst_recommendations(ticker),
        "institutional_holders": get_institutional_holders(ticker)
    }
