"""
UI Package for FinResearch AI
==============================

This package contains the Streamlit-based user interface for the FinResearch AI
multi-agent financial analysis system.

Modules:
--------
- app: Main Streamlit application entry point
- components: UI components for input, output, and export
- utils: Utility functions for state management and formatting

Usage:
------
Run the UI application:
    streamlit run ui/app.py

or use the run script:
    python run_ui.py
"""

__version__ = "1.0.0"
__author__ = "Yan He"

# Import main components for easier access
from ui.utils.state_manager import (
    initialize_session_state,
    update_analysis_state,
    clear_analysis_state
)

from ui.utils.formatters import (
    parse_crew_output,
    extract_executive_summary,
    extract_financial_indicators,
    extract_news_sentiment,
    extract_risks_opportunities
)

__all__ = [
    # State management
    "initialize_session_state",
    "update_analysis_state",
    "clear_analysis_state",
    
    # Formatters
    "parse_crew_output",
    "extract_executive_summary",
    "extract_financial_indicators",
    "extract_news_sentiment",
    "extract_risks_opportunities",
]