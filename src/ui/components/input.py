"""
Input form components for user parameters.
"""

import streamlit as st
from datetime import datetime


def render_input_form() -> dict:
    """
    Render the input form in the sidebar.
    
    Returns:
        dict: User input parameters
    """
    
    # Ticker input
    ticker = st.text_input(
        "Stock Ticker",
        value="AAPL",
        max_chars=10,
        help="Enter stock ticker symbol (e.g., AAPL, TSLA, MSFT)"
    ).upper().strip()
    
    # Investor mode selection
    investor_mode = st.selectbox(
        "Investor Perspective",
        options=["Neutral", "Bullish", "Bearish"],
        index=0,
        help="Select the tone/perspective for the analysis"
    )
    
    # Information display
    st.divider()
    st.caption(f"📅 Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    # Validation
    if not ticker:
        st.warning("⚠️ Please enter a ticker symbol")
    
    return {
        "ticker": ticker,
        "investor_mode": investor_mode,
        #"analysis_depth": analysis_depth.lower(),
        #"include_competitors": include_competitors,
        #"time_horizon": time_horizon,
        "timestamp": datetime.now().isoformat()
    }