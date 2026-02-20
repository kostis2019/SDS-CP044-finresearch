"""Lead Market Researcher agent who gathers accurate, real-time stock data and identifies key market trends."""

from pathlib import Path
import sys
from crewai import Agent, Task
from langchain_openai import ChatOpenAI
from .base import load_prompt

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
from src.tools import get_stock_info, get_stock_price
from src.tools.memory_tools import MemoryTools

def build_financial_analyst() -> Agent:
    """
    Build the financial analyst agent.

    This agent responsibilitie:
    - Pulls APIs for price history
    - Computes:
        P/E, PEG, ROE, ROA
        Revenue/EPS growth
        Volatility & risk measures
    - Writes structured insights

    Tools:
    - Pulls APIs for price history: get stock data inlcuding quote and company info
    - Web Search: For recent earnings reports and analyst coverage

    Returns:
        Configured fanancial analyst agent
    """
    # Load system prompt
    prompt = load_prompt('financial_analyst.md')
    
    agent = Agent(
        role="Financial Analyst",
        goal=f"Gathers accurate, real-time stock data and writes structured insights for stock",
        backstory=(prompt),
        verbose=True,    
        
        # TOOLS: This is the key differentiator! This agent can fetch real data.
        # The agent will automatically decide when to use these tools based on
        # the task description and the tool docstrings.        
        tools=[get_stock_price, get_stock_info, MemoryTools.save_finding],
                
        # ALLOW DELEGATION: Set to False because we want this agent to do the
        # research itself, not delegate to the writer (who has no tools anyway).
        allow_delegation=False,
        
        # LLM: We use GPT-4 with temperature=0 for maximum accuracy.
        # For financial data, we want deterministic, factual responses.
        llm=ChatOpenAI(model_name="gpt-4o-mini", temperature=0),

        #max_iter=10
    )

    return agent

def build_financial_analyst_task(inputs: dict = None) -> Task:
    """
    Build the market researcher task:
    - Pulls APIs for price history
    - Computes:
        P/E, PEG, ROE, ROA
        Revenue/EPS growth
        Volatility & risk measures
    - Writes structured insights
   
    Returns:
        Configured financial analyst task
    """
  
    ticker = inputs.get("ticker") 
    investor_mode = inputs.get("investor_mode")
    
    task = Task(      
       description=(
            f"Conduct a comprehensive financial analysis of {ticker}.\n\n"
            f"Investment Perspective: {investor_mode}\n\n"
            "⚠️ CRITICAL REQUIREMENTS - ALL financial metrics must be obtained:\n\n"
            "STEP 1: Fetch Data\n"
            f"- Use get_stock_price tool to fetch current price for {ticker}\n"
            f"- Use get_stock_info tool to fetch company information including financial metrics for {ticker}\n\n"
            "STEP 2: Extract/Calculate Required Metrics (ALL are mandatory):\n"
            "✓ Current Stock Price\n"
            "✓ P/E Ratio (Price-to-Earnings)\n"
            "✓ PEG Ratio (Price/Earnings to Growth)\n"
            "✓ Debt-to-Equity Ratio\n"
            "✓ ROE (Return on Equity) - REQUIRED\n"
            "✓ ROA (Return on Assets) - REQUIRED\n"
            "✓ Revenue Growth\n"
            "✓ EPS Growth\n"
            "✓ Profit Margin\n"
            "✓ Operating Margin\n\n"
            "STEP 3: Validation\n"
            "- Before proceeding, verify you have obtained ALL metrics listed above\n"
            "- If any metric is missing from API response, mark it as 'N/A' with explanation\n"
            "- Do NOT skip any metric - every field must have a value or 'N/A'\n\n"
            "STEP 4: Save Results\n"
            f"- Use save_finding tool to save ALL metrics to vector database\n"
            "- Include timestamp and confirm all required fields are present\n\n"
            f"Frame your analysis from a {investor_mode.lower()} perspective.\n"
            "Remain objective and data-driven.\n\n"
            "⚠️ IMPORTANT: If get_stock_info doesn't return ROE or ROA, you must:\n"
            "1. Check if the data contains netIncome, totalAssets, shareholderEquity\n"
            "2. Calculate manually: ROE = netIncome / shareholderEquity\n"
            "3. Calculate manually: ROA = netIncome / totalAssets\n"
            "4. If calculation impossible, mark as 'Data not available from source'\n"
        ),
     expected_output=(
            "A structured JSON report containing ALL required financial metrics:\n"
            "{\n"
            "  'ticker': 'TICKER',\n"
            "  'current_price': value,\n"
            "  'pe_ratio': value or 'N/A',\n"
            "  'peg_ratio': value or 'N/A',\n"
            "  'debt_to_equity': value or 'N/A',\n"
            "  'roe': value or 'N/A (with reason)',\n"
            "  'roa': value or 'N/A (with reason)',\n"
            "  'revenue_growth': value or 'N/A',\n"
            "  'eps_growth': value or 'N/A',\n"         
            "  'profit_margin': value or 'N/A',\n"
            "  'operating_margin': value or 'N/A',\n"
            "  'analysis_timestamp': 'ISO timestamp',\n"
            "  'missing_metrics': ['list any N/A metrics with reasons']\n"
            "}\n\n"
            "Every metric must be present in the output, even if marked as N/A."
        ),
    agent=build_financial_analyst()
    )

    return task