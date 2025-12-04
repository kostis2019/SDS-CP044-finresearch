"""Lead Market Researcher agent who gathers accurate, real-time stock data and identifies key market trends."""

from crewai import Agent, Task, Crew, Process
from crewai.tools import tool
import yfinance as yf
from langchain_openai import ChatOpenAI
from .base import load_prompt

@tool("Get Stock Price")
def get_stock_price(ticker: str) -> str:
    """
    Fetches the current stock price for a given ticker symbol.
    
    Use this tool when you need to find the current market price of a stock.
    Input should be a valid stock ticker symbol (e.g., 'AAPL' for Apple, 
    'TSLA' for Tesla, 'GOOGL' for Google).
    
    Args:
        ticker: A stock ticker symbol (uppercase recommended)
    
    Returns:
        A string with the current stock price or an error message
    """
    try:
        # DEFENSIVE CODING: Clean the input to handle common formatting issues
        ticker = ticker.strip().upper()
        
        stock = yf.Ticker(ticker)
        history = stock.history(period="1d")
        
        # EDGE CASE: Handle empty data (invalid ticker or market closed)
        if history.empty:
            return f"No data available for ticker '{ticker}'. Please verify the ticker symbol is correct."
        
        price = history['Close'].iloc[-1]
        
        # CONTEXT ENRICHMENT: Return additional useful information
        company_name = stock.info.get('shortName', ticker)
        return f"The current price of {company_name} ({ticker}) is ${price:.2f} USD"
        
    except Exception as e:
        # GRACEFUL DEGRADATION: Return useful error info instead of crashing
        return f"Error fetching price for '{ticker}': {str(e)}. Please check the ticker symbol."


@tool("Get Stock Info")
def get_stock_info(ticker: str) -> str:
    """
    Fetches detailed company information for a given ticker symbol.
    
    Use this tool when you need background information about a company,
    such as sector, industry, market cap, or business description.
    Input should be a valid stock ticker symbol (e.g., 'AAPL', 'MSFT').
    
    Args:
        ticker: A stock ticker symbol
    
    Returns:
        A string with company details or an error message
    """
    try:
        ticker = ticker.strip().upper()
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # BUILD A STRUCTURED RESPONSE
        # We return key metrics that would be useful for a financial analyst
        return (
            f"Company: {info.get('shortName', 'N/A')}\n"
            f"Sector: {info.get('sector', 'N/A')}\n"
            f"Industry: {info.get('industry', 'N/A')}\n"
            f"Market Cap: ${info.get('marketCap', 0):,.0f}\n"
            f"52-Week High: ${info.get('fiftyTwoWeekHigh', 0):.2f}\n"
            f"52-Week Low: ${info.get('fiftyTwoWeekLow', 0):.2f}"
        )
    except Exception as e:
        return f"Error fetching info for '{ticker}': {str(e)}"

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
        goal="Gathers accurate, real-time stock data and writes structured insights",
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
        llm=ChatOpenAI(model_name="gpt-4", temperature=0)
    )

    return agent

def build_financial_analyst_task() -> Task:
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
    task = Task(
       description=(
        "Research the current market status of user given stock like Tesla (TSLA) and Apple (AAPL)\n"
        "For each stock, find:\n"
        "1. The current stock price\n"
        "2. Basic company information\n"
        "Compile your findings into a structured research report."
    ),
    expected_output=(
        "A structured research report with two sections (one per stock), "
        "each containing the current price and key company metrics. "
        "Include the date/time context that this is real-time data."
    ),
    agent=build_financial_analyst()
    )

    return task