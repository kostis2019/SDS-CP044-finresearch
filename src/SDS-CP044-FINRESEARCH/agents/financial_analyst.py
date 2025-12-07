"""Lead Market Researcher agent who gathers accurate, real-time stock data and identifies key market trends."""

from crewai import Agent, Task
from langchain_openai import ChatOpenAI
from .base import load_prompt
from .tools.financial_tools import get_stock_info, get_stock_price

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
        tools=[get_stock_price, get_stock_info],
                
        # ALLOW DELEGATION: Set to False because we want this agent to do the
        # research itself, not delegate to the writer (who has no tools anyway).
        allow_delegation=False,
        
        # LLM: We use GPT-4 with temperature=0 for maximum accuracy.
        # For financial data, we want deterministic, factual responses.
        llm=ChatOpenAI(model_name="gpt-4o-mini", temperature=0)
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
            "Your analysis must include:\n"
            "- Fetch stock price and stock info\n"
            "- Key valuation metrics (P/E, PEG, Debt/Equity)\n"
            "- Growth metrics (revenue growth, EPS growth)\n"
            "- Risk flags (LLM-estimated)\n\n"            
            f"Frame your analysis from a {investor_mode.lower()} perspective, "
            "but remain objective and data-driven.\n\n"
            "Use the available tools to fetch real-time stock data and calculate metrics."
       ),
    expected_output=(
        "A structured research report with two sections (one per stock), "
        "each containing the current price and key company metrics. "
        "Include the date/time context that this is real-time data."
    ),
    agent=build_financial_analyst()
    )

    return task