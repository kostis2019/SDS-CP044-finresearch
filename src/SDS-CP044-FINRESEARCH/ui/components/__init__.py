"""
UI Components Package
=====================

Contains reusable Streamlit components for the FinResearch AI interface.

Components:
-----------
- input_form: User input collection components
- output_tabs: Results display in tabbed interface
- export_buttons: Export functionality for reports
"""

from ui.components.input import render_input_form
from ui.components.output import (
    render_output_tabs,
    render_executive_summary,
    render_financial_indicators,
    render_news_sentiment,
    render_risks_opportunities,
    render_full_report
)
from ui.components.export import (
    render_export_buttons,
    generate_markdown_report,
    format_list_items
)

__all__ = [
    # Input components
    "render_input_form",
    
    # Output components
    "render_output_tabs",
    "render_executive_summary",
    "render_financial_indicators",
    "render_news_sentiment",
    "render_risks_opportunities",
    "render_full_report",
    
    # Export components
    "render_export_buttons",
    "generate_markdown_report",
    "format_list_items",
]