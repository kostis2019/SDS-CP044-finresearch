from crewai.tools import tool
from config.settings import get_config
import yfinance as yf
from tavily import TavilyClient

def roundNumericalString(value: str, ndigits: int) -> str:
    result = 'N/A'
    if value is None:
        return result        
    
    if isinstance(value, (int, float)):
        result = round(value, ndigits)
    
    return result
    

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
        #print(f"stock price of {ticker}" + "\n")        
        print(price)
        #print(f"stock price of {ticker}" + "\n")
    
        
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
        #print(f"stock info of {ticker}"  + "\n")        
        #print(info)        
        #print(f"stock info of {ticker}" + "\n")

      
        # Extract and round P/E ratio to 2 decimal places
        """    trailing_pe = info.get('trailingPE')
        if trailing_pe is not None and isinstance(trailing_pe, (int, float)):
            trailing_pe = round(trailing_pe, 2)
        else:
            trailing_pe = 'N/A'
        print(f"trailing_pe: ${trailing_pe}")    """     
        
        # BUILD A STRUCTURED RESPONSE
        # We return key metrics that would be useful for a financial analyst
        # Ensure critical metrics are included
        stock_info = {
            'ticker': ticker,
            'company_name': info.get('longName', 'N/A'),

            'sector': info.get('sector', 'N/A'),
            'industry': info.get('industry', 'N/A'),
            'market_cap': info.get('marketCap', 0),            
            '52-week_range': info.get('fiftyTwoWeekRange', 0),
                    
            # Valuation metrics
            'pe_ratio': f"{info.get('trailingPE', 'N/A'):.2f}",
            #'pe_ratio': roundNumericalString(info.get('trailingPE')),
            #'peg_ratio': roundNumericalString(info.get('trailingPegRatio', 2)),
            'peg_ratio': f"{info.get('trailingPegRatio', 'N/A'):.2f}",
            'debt_to_equity': f"{info.get('debtToEquity', 'N/A'):.2f}",
            
            # Profitability metrics - CRITICAL
            'roe': f"{info.get('returnOnEquity', 'N/A'):.2f}",
            'roa': f"{info.get('returnOnAssets', 'N/A'):.2f}",
            
            # If ROE/ROA missing, provide raw data for calculation
            'net_income': info.get('netIncomeToCommon', 'N/A'),
            'total_assets': info.get('totalAssets', 'N/A'),
            'shareholder_equity': info.get('totalStockholderEquity', 'N/A'),

            'revenue_growth': info.get('revenueGrowth', 'N/A'),
            'eps_growth': info.get('trailingEps', 'N/A'),
            
            # Other metrics
            'profit_margin': info.get('profitMargins', 'N/A'),
            'operating_margin': info.get('operatingMargins', 'N/A'),
           
            # Full info for agent to explore
            'full_info': info
        }     

        return stock_info       
    except Exception as e:
        return f"Error fetching info for '{ticker}': {str(e)}"

@tool("Get Market Data")
def get_market_data(ticker: str) -> str:
    """
    Fetches the current market data for a given ticker symbol.

    Use this tool when you need to find the current market data.
    Input should be a valid user given stock ticker symbol (e.g., 'AAPL' for Apple).

    Args:
    ticker: A stock ticker symbol (uppercase recommended)

    Returns:
    A string with the current market data or an error message
    """
    try:        
        config = get_config()
        ticker = ticker.strip().upper()
        tavily_client = TavilyClient(config['tavily_api_key'])
        market_query = f"Bring up some of the latest market data for stock {ticker}"

        search_response = tavily_client.search(market_query)
        #print("Tavily search result:" + "\n")
        #print(search_response)
        #print("Tavily search result:" + "\n")

        market_data = ""
        for result in search_response["results"]:
            market_data += f"### {result['title']}\n\n{result['content']}\n\n"

        return f"""
            The current market data for ({ticker})\n
            {market_data}
            """
    
    except Exception as e:
        # GRACEFUL DEGRADATION: Return useful error info instead of crashing
        return f"Error fetching market data for '{ticker}': {str(e)}. Please check the ticker symbol."