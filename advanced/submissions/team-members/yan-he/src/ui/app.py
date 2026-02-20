"""
FinResearch AI - Streamlit UI
Main application entry point for the multi-agent financial research system.
"""

import streamlit as st
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents import build_financial_crew
from ui.components.input import render_input_form
from ui.components.output import render_output_tabs
from ui.components.export import render_export_buttons
from ui.utils.state_manager import initialize_session_state, update_analysis_state
from ui.utils.formatters import parse_crew_output


def main():
    """Main Streamlit application."""
    
    # Page configuration
    st.set_page_config(
        page_title="FinResearch AI",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    initialize_session_state()
    
    # Header
    st.title("📊 FinResearch AI")
    st.markdown("*Automated Financial Market Intelligence with Multi-Agent Systems*")    
    st.divider()
    
    # Sidebar - Input Form
    with st.sidebar:
        st.header("🔍 Research Parameters")
        
        # Render input form and get user inputs
        user_inputs = render_input_form()
        
        # Run Analysis Button
        if st.button("🚀 Run Analysis", type="primary", use_container_width=True):
            run_analysis(user_inputs)
        
        st.divider()
        st.info(
        "⚠️ **Disclaimer:** This tool is for informational purposes only and does not constitute financial advice. "
        "The information provided should not be relied upon as a substitute for professional financial advice. "
        "Always consult with a qualified financial advisor before making investment decisions."
    )    
 
    
    analysis_complete = st.session_state.get("analysis_complete", False) 
    # Main content area
    if st.session_state.get("analysis_complete", False):
      
        analysis_results_from_get = st.session_state.get("analysis_results")
       
        
        # Display results in tabs
        render_output_tabs(st.session_state.get("analysis_results"))
                        
        # Export options
        st.divider()
        render_export_buttons(st.session_state.get("analysis_results"))
    else:
        # Welcome screen
        render_welcome_screen()


def run_analysis(user_inputs: dict):
    """
    Execute the financial analysis using CrewAI agents.
    
    Args:
        user_inputs: Dictionary containing ticker and investor_mode
    """
    try:
        # Show progress
        with st.spinner("🤖 AI Agents are analyzing... This may take about one minute."):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Update progress
            status_text.text("Initializing crew...")
            progress_bar.progress(20)            
                       
            # Update progress
            status_text.text("Manager delegating tasks...")
            progress_bar.progress(40)
            
            # Prepare inputs for the crew
            user_inputs = {
                "ticker": user_inputs["ticker"],
                "investor_mode": user_inputs["investor_mode"],
                "analysis_depth": user_inputs.get("analysis_depth", "standard")
            }

             # Build the crew
            crew = build_financial_crew(user_inputs)
            
            # Update progress
            status_text.text("Agents researching and analyzing...")
            progress_bar.progress(60)
            
            # Execute the crew
            result = crew.kickoff()         
            
            # Update progress
            status_text.text("Formatting results...")
            progress_bar.progress(80)
            
            # Parse and structure the output           
            structured_results = parse_crew_output(result, user_inputs)

            #print("structured_results" * 3)           
            #print(structured_results)
            #print("structured_results" * 70 + "\n")
            
            # Update progress
            progress_bar.progress(100)
            status_text.text("Analysis complete!")
            
            # Store results in session state
            update_analysis_state(structured_results)
            
            # Success message
            st.success("✅ Analysis completed successfully!")
            st.rerun()
            
    except Exception as e:
        st.error(f"❌ Error during analysis: {str(e)}")
        st.exception(e)


def render_welcome_screen():
    """Display welcome screen with instructions."""
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ## Welcome to FinResearch AI 🎯
        
        This AI-powered platform uses multiple specialized agents to provide 
        comprehensive financial market intelligence:
        
        ### 🤖 Our Agent Team:
        
        1. **Manager Agent** - Orchestrates the research process and ensures quality
        2. **Researcher Agent** - Scrapes web, news, and analyst commentary
        3. **Financial Analyst Agent** - Gathers quantitative metrics and ratios
        4. **Reporting Agent** - Synthesizes findings into professional reports
        
        ### 📋 How to Use:
        
        1. Enter a stock ticker (e.g., AAPL, TSLA) in the sidebar
        2. Select your investor perspective
        3. Click "Run Analysis" to start
        4. Review results across organized tabs
        5. Export reports in your preferred format
        
        ---
        
        **Ready to get started?** Enter your research parameters in the sidebar! 👈
        """)
    
    with col2:
        st.info("""
        ### 💡 Quick Tips
        
        - **Neutral Mode**: Objective analysis
        - **Bullish Mode**: Growth-focused perspective
        - **Bearish Mode**: Risk-focused perspective
        
        Analysis typically takes around 1 minute depending on complexity.
        """)
        
        # Example tickers
        st.markdown("### 📈 Popular Tickers")
        st.code("AAPL, TSLA, MSFT, GOOGL, AMZN, NVDA, META")


if __name__ == "__main__":
    main()