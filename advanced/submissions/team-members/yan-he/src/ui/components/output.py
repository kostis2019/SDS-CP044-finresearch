"""
Output display components organized in tabs.
"""

import streamlit as st
import pandas as pd

def apply_custom_css():
    """Apply custom CSS to reduce metric font sizes across all tabs."""
    st.markdown("""
        <style>
        /* Reduce metric value font size */
        [data-testid="stMetricValue"] {
            font-size: 20px !important;
        }
        
        /* Reduce metric label font size */
        [data-testid="stMetricLabel"] {
            font-size: 13px !important;
        }
        
        /* Reduce metric delta font size */
        [data-testid="stMetricDelta"] {
            font-size: 11px !important;
        }
        </style>
    """, unsafe_allow_html=True)

def render_output_tabs(results: dict):
    """
    Render analysis results in organized tabs.
    
    Args:
        results: Dictionary containing structured analysis results
    """
    
    if not results:
        st.warning("No results to display")
        return  

    # Create tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 Executive Summary",
        "📊 Financial Indicators",
        "📰 News & Sentiment",
        "⚠️ Risks & Opportunities",
        "📄 Full Report"
    ])
  
    # Tab 1: Executive Summary
    with tab1:     
        render_executive_summary(results.get("executive_summary", {}))
    
    # Tab 2: Financial Indicators
    with tab2:
        render_financial_indicators(results.get("financial_indicators", {}))
    
    # Tab 3: News & Sentiment
    with tab3:
        render_news_sentiment(results.get("news_sentiment", {}))
    
    # Tab 4: Risks & Opportunities
    with tab4:
        render_risks_opportunities(results.get("risks_opportunities", {}))
    
    # Tab 5: Full Report
    with tab5:
        render_full_report(results.get("full_report", ""))


def render_executive_summary(summary: dict):
    """Render the executive summary tab."""
    
    st.header("Executive Summary")
    
    col1, col2, col3 = st.columns(3)  
  
    summary_price = summary.get("current_price", "N/A")  
    
    with col1:
        st.metric(
            "Current Price",
            summary.get("current_price", "N/A"),
            #summary.get("price_change", "N/A")
        )
    
    with col2:
        st.metric(
            "Recommendation",
            summary.get("recommendation", "N/A")
        )
    
    with col3:
        st.metric(
            "Risk Level",
            summary.get("risk_level", "N/A")
        )
    
    st.divider()
    
    st.subheader("Key Takeaways")
    st.markdown(summary.get("key_takeaways", "No summary available."))
    
    st.subheader("Investment Thesis")
    st.markdown(summary.get("investment_thesis", "No thesis available."))


def render_financial_indicators(indicators: dict):
    """Render the financial indicators tab."""
     # Apply custom CSS styling - call once here to affect all tabs
    apply_custom_css()
    
    st.header("Financial Indicators")  
    
    # Valuation Metrics
    st.subheader("📈 Valuation Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("P/E Ratio", indicators.get("pe_ratio", "N/A"))
    with col2:
        st.metric("PEG Ratio", indicators.get("peg_ratio", "N/A"))
    with col3:
        #st.metric("P/B Ratio", indicators.get("pb_ratio", "N/A"))
        st.metric("Debt/Equity", indicators.get("debt_to_equity", "N/A"))
    #with col4:
        #st.metric("EV/EBITDA", indicators.get("ev_ebitda", "N/A"))
    
    st.divider()
    
    # Profitability Metrics
    st.subheader("💰 Profitability Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("ROE", indicators.get("roe", "N/A"))
    with col2:
        st.metric("ROA", indicators.get("roa", "N/A"))
    with col3:
        st.metric("Profit Margin", indicators.get("profit_margin", "N/A"))
    with col4:
        st.metric("Operating Margin", indicators.get("operating_margin", "N/A"))
    
    st.divider()
    
    # Growth Metrics
    st.subheader("📊 Growth Metrics")
    
    if indicators.get("growth_data"):
        df = pd.DataFrame(indicators["growth_data"])
        st.dataframe(df, use_container_width=True) #st.dataframe(df, width=True)        
    else:
        st.info("No growth data available")
    
    # Volatility & Risk
    st.subheader("⚡ Volatility & Risk Measures")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Beta", indicators.get("beta", "N/A"))
    with col2:
        st.metric("52-Week Volatility", indicators.get("volatility", "N/A"))
    with col3:
        st.metric("Sharpe Ratio", indicators.get("sharpe_ratio", "N/A"))


def render_news_sentiment(news: dict):
    """Render the news and sentiment tab."""
    
    st.header("News & Sentiment Analysis")
    
    # Sentiment Overview
    col1, col2, col3 = st.columns(3)
    
    with col1:
        sentiment_score = news.get("sentiment_score", 0)
        st.metric("Overall Sentiment", f"{sentiment_score:.2f}", 
                 delta=news.get("sentiment_trend", ""))
    
    with col2:
        st.metric("News Volume", news.get("news_count", "N/A"))
    
    with col3:
        st.metric("Social Buzz", news.get("social_mentions", "N/A"))
    
    st.divider()
    
    # Recent News
    st.subheader("📰 Recent News Headlines")
    
    news_items = news.get("news_items", [])
    if news_items:
        for item in news_items:
            with st.expander(f"**{item.get('title', 'Untitled')}** - {item.get('date', '')}"):
                st.markdown(item.get('summary', 'No summary available.'))
                st.caption(f"Source: {item.get('source', 'Unknown')} | Sentiment: {item.get('sentiment', 'Neutral')}")
    else:
        st.info("No recent news available")
    
    # Analyst Ratings
    st.subheader("👔 Analyst Consensus")
    analyst_data = news.get("analyst_ratings", {})
    
    if analyst_data:
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Buy Ratings", analyst_data.get("buy", "N/A"))
            st.metric("Hold Ratings", analyst_data.get("hold", "N/A"))
            st.metric("Sell Ratings", analyst_data.get("sell", "N/A"))
        
        with col2:
            st.metric("Average Price Target", analyst_data.get("avg_target", "N/A"))
            st.metric("Consensus Rating", analyst_data.get("consensus", "N/A"))


def render_risks_opportunities(data: dict):
    """Render the risks and opportunities tab."""
    
    st.header("Risks & Opportunities")
    
    col1, col2 = st.columns(2)
    
    # Opportunities
    with col1:
        st.subheader("🚀 Opportunities")
        opportunities = data.get("opportunities", [])
        if opportunities:
            for opp in opportunities:
                st.success(f"**{opp.get('title', '')}**")
                st.markdown(opp.get('description', ''))
                st.caption(f"Impact: {opp.get('impact', 'Medium')} | Probability: {opp.get('probability', 'Medium')}")
                st.divider()
        else:
            st.info("No opportunities identified")
    
    # Risks
    with col2:
        st.subheader("⚠️ Risks")
        risks = data.get("risks", [])
        if risks:
            for risk in risks:
                st.error(f"**{risk.get('title', '')}**")
                st.markdown(risk.get('description', ''))
                st.caption(f"Impact: {risk.get('impact', 'Medium')} | Probability: {risk.get('probability', 'Medium')}")
                st.divider()
        else:
            st.info("No significant risks identified")
    
    # SWOT Analysis
    st.subheader("📊 SWOT Analysis")
    swot = data.get("swot", {})
    
    col1, col2 = st.columns(2)
    
    with col1:
        with st.container(border=True):
            st.markdown("**Strengths**")
            for item in swot.get("strengths", []):
                st.markdown(f"- {item}")
        
        with st.container(border=True):
            st.markdown("**Opportunities**")
            for item in swot.get("opportunities", []):
                st.markdown(f"- {item}")
    
    with col2:
        with st.container(border=True):
            st.markdown("**Weaknesses**")
            for item in swot.get("weaknesses", []):
                st.markdown(f"- {item}")
        
        with st.container(border=True):
            st.markdown("**Threats**")
            for item in swot.get("threats", []):
                st.markdown(f"- {item}")


def render_full_report(report: str):
    """Render the full markdown report."""
    
    st.header("Full Report")
    
    if report:
        st.markdown(report)
    else:
        st.info("No full report available")