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
    
    # Optional: Analysis depth
    with st.expander("⚙️ Advanced Options"):
        analysis_depth = st.select_slider(
            "Analysis Depth",
            options=["Quick", "Standard", "Deep"],
            value="Standard",
            help="Control the thoroughness of the research"
        )
        
        include_competitors = st.checkbox(
            "Include Competitor Analysis",
            value=False,
            help="Compare with industry peers"
        )
        
        time_horizon = st.selectbox(
            "Investment Horizon",
            options=["Short-term (< 1 year)", "Medium-term (1-3 years)", "Long-term (3+ years)"],
            index=1
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
        "analysis_depth": analysis_depth.lower(),
        "include_competitors": include_competitors,
        "time_horizon": time_horizon,
        "timestamp": datetime.now().isoformat()
    }