"""Reporter agent who produces financial report"""

from pathlib import Path
import sys
from crewai import Agent, Task
from langchain_openai import ChatOpenAI
from .base import load_prompt

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.tools.memory_tools import MemoryTools

def build_reporter() -> Agent:
    """
    Build the reported agent.

    This agent responsibilitie:
    1. Executive Summary (≤150 words)
    2. Company Snapshot
    - Sector, market position, competitors
    3. Key Financial Indicators
    - Price movements
    - Valuation ratios
    - Profitability ratios
    4. Recent News & Sentiment
    5. Opportunities (Bull Case)
    6. Risks (Bear Case)
    7. Final Perspective

    Tools:
    - Memory Tool: Query final results saved in vestor DB

    Returns:
        Configured reported agent
    """
    # Load system prompt
    prompt = load_prompt('reporter.md')
    
    agent = Agent(
        role="Financial Reporter",
        goal=f"Produces financial report based on the final results from Financial Analyst and Merket Researcher",
        backstory=(prompt),                
        tools=[MemoryTools.search_memory],
        verbose=True,
    )

    return agent

def build_reporter_task(inputs: dict = None, context: list = None) -> Task:
    """
    Build the reporter task:
    1. Executive Summary (≤150 words)
    2. Company Snapshot
    - Sector, market position, competitors
    3. Key Financial Indicators
    - Price movements
    - Valuation ratios
    - Profitability ratios
    4. Recent News & Sentiment
    5. Opportunities (Bull Case)
    6. Risks (Bear Case)
    7. Final Perspective

    Returns:
        Configured reporter task
    """
    ticker = inputs.get("ticker")

    task = Task(      
       description=(
        f"⚠ Important: This task can ONLY start after BOTH the financial analyst \n"
         "and market researcher have COMPLETED their analysis and SAVED results to the vector database.\n\n"
        f"Produce financial report for {ticker}, which is based on saved results from financial analyst and market researcher.\n\n"
            f"First, you query the vector database\n\n"
            "Your responsibilities must include:\n"
            "1. Executive Summary (≤150 words)\n"
            "2. Company Snapshot\n"
            "- Sector, market position, competitors\n"
            "3. Key Financial Indicators\n"
            "- Price movements\n"
            "- Valuation ratios\n"
            "- Profitability ratios\n"
            "4. Recent News & Sentiment\n"
            "5. Opportunities (Bull Case)\n"
            "6. Risks (Bear Case)\n"
            "7. Final Perspective\n\n"
            f"No need to query vector database again if the queried data are already returned from the  databas\n\n"                  
        ),
        expected_output=(
            "A structured report in JSON format including following sections:\n"
            "Executive Summary\n"
            "Financial Indicators\n"
            "Under the Financial Indicators section, for some sub-sections like Valuation Retios\n"
            "and Profitability Ratios, use the following key values\n"
            "'P/E Ratio': value or 'N/A'\n"
            "'PEG Ratio': value or 'N/A'\n"
            "'Debt-to-Equity': value or 'N/A'\n"
            "'ROE': value or 'N/A'\n"
            "'ROA': value or 'N/A'\n"
            "'Revenue Growth': value or 'N/A'\n"
            "'EPS Growth': value or 'N/A'\n"
            "News & Sentiment\n"
            "Risks & Opportunities\n"
            "Full Report (Markdown)\n\n"
        ),        
        agent=build_reporter(),

        # Use outputs of tasks from financial_analyst and market_researcher   
        context=context,

        # Wait for financial analyst and market researcher compplete their tasks
        #async_execution=False 
    )

    return task