from crewai.tools import tool
import yfinance as yf

@tool("Get Stock Price")
def get_stock_price(ticker: str) -> str:
    """
    Fetches the current stock price for a given ticker symbol.
    
    Use this tool when you need to find the current market price of a user given stock.
    Input should be a valid stock ticker symbol (e.g., 'AAPL' for Apple).
    
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
        print(f"---------stock price of {ticker}" + "\n")        
        print(price)
        print(f"---------stock price of {ticker}" + "\n")
    
        
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
    Input should be a valid stock ticker symbol (e.g., 'AAPL').
    
    Args:
        ticker: A stock ticker symbol
    
    Returns:
        A string with company details or an error message
    """
    try:
        ticker = ticker.strip().upper()
        stock = yf.Ticker(ticker)
        info = stock.info
        print(f"---------stock info of {ticker}" + "\n")        
        print(info)
        print(f"---------stock info of {ticker}" + "\n")
        
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