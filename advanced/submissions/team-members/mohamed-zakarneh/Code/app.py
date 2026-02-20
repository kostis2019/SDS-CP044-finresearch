import streamlit as st
from backend import run_financial_agent
import time

result = None

st.set_page_config(
    page_title="AI Financial Research Agent",
    page_icon="📊",
    layout="wide"
)

st.title("📊 AI Financial Research Agent")
st.markdown(
"""
<div style="font-size: 0.85rem; line-height: 1.3;">
Multi-agent investment research prototype (Manager → Researcher → Analyst → Reporter).<br>
⚠️ <b>Prototype warning:</b> This system analyzes financial data.
It is not your personal risk-free advisor or life goals achiever.<br>
It produces research summaries — not investment advice.<br>
If it makes you rich, that was luck. If it loses money, that was math.<br><br>
</div>
""",
    unsafe_allow_html=True
)

user_query = st.text_area(
    "Enter your financial question",
    placeholder="Compare Emerson and Honeywell stocks",
    height=120
)

run = st.button("Run Analysis", type="primary")

if run:
    if not user_query.strip():
        st.warning("Please enter a financial query.")
        st.stop()

if run:
    with st.status("Running multi-agent analysis…", expanded=True) as status:
        start = time.time()

        try:
            result = run_financial_agent(user_query)

            status.update(
                label=f"Analysis completed in {round(time.time() - start, 2)}s",
                state="complete"
            )

        except Exception as e:
            status.update(label="Analysis failed", state="error")
            st.exception(e)
            st.stop()

if result:
    tab_report, tab_sources = st.tabs(["📄 Report", "📚 Sources"])
    st.subheader("🔎 Request Understanding")

    with tab_report:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Objective**")
            objective = result.get("objective")
            st.code(f"{objective['route']}, {objective['reason']} " or "N/A")
        with col2:
            st.markdown("**Tickers Detected**")
            tickers = result.get("tickers") or []
            st.code(", ".join(tickers) if tickers else "None")
        st.markdown(result.get("final_report", "No report generated."))
   
    with tab_sources:
        st.markdown("### Data & Research Sources")
        ro = result["raw_state"].get("researcher_outputs", {})
        companies = ro.get("companies", {})
        for ticker, tools_output in companies.items():
            st.markdown(f"#### {ticker}")
            for tool_name in ['web_search', 'yahoo_finance_news', 'yahoo_finance_stats']:
                content =  tools_output[tool_name]
                if isinstance(content,tuple):
                    content = content[0]
                with st.expander(tool_name):
                    if isinstance(content, dict):
                        st.json(content)
                    else:
                        st.markdown(content)