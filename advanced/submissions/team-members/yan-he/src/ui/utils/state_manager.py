"""
Session state management utilities.
"""

import streamlit as st


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    
    if "analysis_complete" not in st.session_state:
        st.session_state.analysis_complete = False
    
    if "analysis_results" not in st.session_state:
        st.session_state.analysis_results = None
    
    if "analysis_history" not in st.session_state:
        st.session_state.analysis_history = []


def update_analysis_state(results: dict):
    """
    Update session state with new analysis results.
    
    Args:
        results: Dictionary containing analysis results
    """
    st.session_state.analysis_complete = True
    st.session_state.analysis_results = results

    # Add to history
    st.session_state.analysis_history.append({
        "ticker": results.get("ticker"),
        "timestamp": results.get("timestamp"),
        "results": results
    })


def clear_analysis_state():
    """Clear current analysis from session state."""
    
    st.session_state.analysis_complete = False
    st.session_state.analysis_results = None