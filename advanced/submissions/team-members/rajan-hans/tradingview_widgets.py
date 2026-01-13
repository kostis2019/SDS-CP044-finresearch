# tradingview_widgets.py
# TradingView Widget Integration for Streamlit
# 
# These widgets are FREE and don't require an API key.
# They embed directly via iframe/JavaScript.
# 
# Usage:
#   from tradingview_widgets import (
#       render_mini_chart,
#       render_advanced_chart,
#       render_technical_analysis,
#       render_symbol_overview,
#       render_ticker_tape,
#       render_fundamental_data,
#       render_symbol_info,
#   )
#   
#   render_advanced_chart("AAPL", streamlit_container)
# -----------------------------------------------------------------------------

import streamlit as st
import streamlit.components.v1 as components


def render_mini_chart(
    symbol: str,
    width: str = "100%",
    height: int = 220,
    color_theme: str = "light",
    autosize: bool = True,
) -> None:
    """
    Render a TradingView Mini Chart widget.
    
    Simple, compact chart showing price movement.
    Good for: Dashboard headers, quick price overview.
    
    Args:
        symbol: Stock symbol (e.g., "AAPL" or "NASDAQ:AAPL")
        width: Widget width (CSS value)
        height: Widget height in pixels
        color_theme: "light" or "dark"
        autosize: If True, widget auto-sizes to container
    """
    # Add exchange prefix if not present
    if ":" not in symbol:
        symbol = f"NASDAQ:{symbol}"
    
    widget_html = f"""
    <!-- TradingView Widget BEGIN -->
    <div class="tradingview-widget-container">
      <div class="tradingview-widget-container__widget"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-mini-symbol-overview.js" async>
      {{
        "symbol": "{symbol}",
        "width": "{width}",
        "height": "{height}",
        "locale": "en",
        "dateRange": "12M",
        "colorTheme": "{color_theme}",
        "isTransparent": false,
        "autosize": {str(autosize).lower()},
        "largeChartUrl": ""
      }}
      </script>
    </div>
    <!-- TradingView Widget END -->
    """
    
    components.html(widget_html, height=height + 20)


def render_advanced_chart(
    symbol: str,
    width: str = "100%",
    height: int = 500,
    color_theme: str = "light",
    interval: str = "D",
    timezone: str = "America/New_York",
    style: str = "1",
    show_toolbar: bool = True,
    allow_symbol_change: bool = True,
    studies: list = None,
) -> None:
    """
    Render a TradingView Advanced Chart widget.
    
    Full-featured interactive chart with drawing tools.
    Good for: Detailed technical analysis, main chart view.
    
    Args:
        symbol: Stock symbol (e.g., "AAPL" or "NASDAQ:AAPL")
        width: Widget width (CSS value)
        height: Widget height in pixels
        color_theme: "light" or "dark"
        interval: Timeframe - "1", "5", "15", "30", "60", "D", "W", "M"
        timezone: Timezone for the chart
        style: Chart style - "1" (candles), "2" (line), "3" (area), etc.
        show_toolbar: Show top toolbar
        allow_symbol_change: Allow user to change symbol
        studies: List of technical indicators to show
                 e.g., ["RSI@tv-basicstudies", "MASimple@tv-basicstudies"]
    """
    if ":" not in symbol:
        symbol = f"NASDAQ:{symbol}"
    
    # Default studies if none provided
    if studies is None:
        studies = []
    
    studies_json = str(studies).replace("'", '"')
    
    widget_html = f"""
    <!-- TradingView Widget BEGIN -->
    <div class="tradingview-widget-container" style="height:{height}px;width:{width}">
      <div id="tradingview_chart" style="height:calc(100% - 32px);width:100%"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget(
      {{
        "autosize": true,
        "symbol": "{symbol}",
        "interval": "{interval}",
        "timezone": "{timezone}",
        "theme": "{color_theme}",
        "style": "{style}",
        "locale": "en",
        "toolbar_bg": "#f1f3f6",
        "enable_publishing": false,
        "allow_symbol_change": {str(allow_symbol_change).lower()},
        "hide_top_toolbar": {str(not show_toolbar).lower()},
        "hide_legend": false,
        "save_image": true,
        "studies": {studies_json},
        "container_id": "tradingview_chart"
      }}
      );
      </script>
    </div>
    <!-- TradingView Widget END -->
    """
    
    components.html(widget_html, height=height)


def render_technical_analysis(
    symbol: str,
    width: str = "100%",
    height: int = 450,
    color_theme: str = "light",
    interval: str = "1D",
    show_interval_tabs: bool = True,
) -> None:
    """
    Render a TradingView Technical Analysis widget.
    
    Shows buy/sell/neutral gauge based on technical indicators.
    Good for: Quick technical sentiment, Charts tab.
    
    Args:
        symbol: Stock symbol (e.g., "AAPL" or "NASDAQ:AAPL")
        width: Widget width (CSS value)  
        height: Widget height in pixels
        color_theme: "light" or "dark"
        interval: Analysis interval - "1m", "5m", "15m", "1h", "4h", "1D", "1W", "1M"
        show_interval_tabs: Show interval selection tabs
    """
    if ":" not in symbol:
        symbol = f"NASDAQ:{symbol}"
    
    widget_html = f"""
    <!-- TradingView Widget BEGIN -->
    <div class="tradingview-widget-container">
      <div class="tradingview-widget-container__widget"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>
      {{
        "interval": "{interval}",
        "width": "{width}",
        "isTransparent": false,
        "height": "{height}",
        "symbol": "{symbol}",
        "showIntervalTabs": {str(show_interval_tabs).lower()},
        "displayMode": "single",
        "locale": "en",
        "colorTheme": "{color_theme}"
      }}
      </script>
    </div>
    <!-- TradingView Widget END -->
    """
    
    components.html(widget_html, height=height + 20)


def render_symbol_overview(
    symbol: str,
    width: str = "100%",
    height: int = 180,
    color_theme: str = "light",
    chart_type: str = "area",
    show_floating_tooltip: bool = True,
) -> None:
    """
    Render a TradingView Symbol Overview widget.
    
    Compact view with price, change, and mini chart.
    Good for: Page headers, stock summary cards.
    
    Args:
        symbol: Stock symbol (e.g., "AAPL" or "NASDAQ:AAPL")
        width: Widget width (CSS value)
        height: Widget height in pixels
        color_theme: "light" or "dark"
        chart_type: "area" or "candlesticks"
        show_floating_tooltip: Show tooltip on hover
    """
    if ":" not in symbol:
        symbol = f"NASDAQ:{symbol}"
    
    widget_html = f"""
    <!-- TradingView Widget BEGIN -->
    <div class="tradingview-widget-container">
      <div class="tradingview-widget-container__widget"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-symbol-overview.js" async>
      {{
        "symbols": [
          ["{symbol}|1D"]
        ],
        "chartOnly": false,
        "width": "{width}",
        "height": "{height}",
        "locale": "en",
        "colorTheme": "{color_theme}",
        "autosize": true,
        "showVolume": false,
        "showMA": false,
        "hideDateRanges": false,
        "hideMarketStatus": false,
        "hideSymbolLogo": false,
        "scalePosition": "right",
        "scaleMode": "Normal",
        "fontFamily": "-apple-system, BlinkMacSystemFont, Trebuchet MS, Roboto, Ubuntu, sans-serif",
        "fontSize": "10",
        "noTimeScale": false,
        "valuesTracking": "1",
        "changeMode": "price-and-percent",
        "chartType": "{chart_type}",
        "lineWidth": 2,
        "lineType": 0,
        "dateRanges": [
          "1d|1",
          "1m|30",
          "3m|60",
          "12m|1D",
          "60m|1W",
          "all|1M"
        ]
      }}
      </script>
    </div>
    <!-- TradingView Widget END -->
    """
    
    components.html(widget_html, height=height + 20)


def render_ticker_tape(
    symbols: list = None,
    color_theme: str = "light",
    display_mode: str = "adaptive",
    show_symbol_logo: bool = True,
) -> None:
    """
    Render a TradingView Ticker Tape widget.
    
    Scrolling ticker showing multiple symbols.
    Good for: Page headers, market overview.
    
    Args:
        symbols: List of symbols (default: major indices + popular stocks)
        color_theme: "light" or "dark"
        display_mode: "adaptive", "regular", or "compact"
        show_symbol_logo: Show company logos
    """
    if symbols is None:
        symbols = [
            {"proName": "FOREXCOM:SPXUSD", "title": "S&P 500"},
            {"proName": "NASDAQ:NDX", "title": "Nasdaq 100"},
            {"proName": "FOREXCOM:DJI", "title": "Dow Jones"},
            {"proName": "NASDAQ:AAPL", "title": "Apple"},
            {"proName": "NASDAQ:GOOGL", "title": "Google"},
            {"proName": "NASDAQ:MSFT", "title": "Microsoft"},
            {"proName": "NASDAQ:AMZN", "title": "Amazon"},
        ]
    
    symbols_json = str(symbols).replace("'", '"')
    
    widget_html = f"""
    <!-- TradingView Widget BEGIN -->
    <div class="tradingview-widget-container">
      <div class="tradingview-widget-container__widget"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js" async>
      {{
        "symbols": {symbols_json},
        "showSymbolLogo": {str(show_symbol_logo).lower()},
        "isTransparent": false,
        "displayMode": "{display_mode}",
        "colorTheme": "{color_theme}",
        "locale": "en"
      }}
      </script>
    </div>
    <!-- TradingView Widget END -->
    """
    
    components.html(widget_html, height=78)


def render_fundamental_data(
    symbol: str,
    width: str = "100%",
    height: int = 830,
    color_theme: str = "light",
    display_mode: str = "regular",
) -> None:
    """
    Render a TradingView Fundamental Data widget.
    
    Shows key financial metrics and ratios.
    Good for: Fundamentals tab, detailed financial view.
    
    Args:
        symbol: Stock symbol (e.g., "AAPL" or "NASDAQ:AAPL")
        width: Widget width (CSS value)
        height: Widget height in pixels
        color_theme: "light" or "dark"
        display_mode: "regular" or "compact"
    """
    if ":" not in symbol:
        symbol = f"NASDAQ:{symbol}"
    
    widget_html = f"""
    <!-- TradingView Widget BEGIN -->
    <div class="tradingview-widget-container">
      <div class="tradingview-widget-container__widget"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-financials.js" async>
      {{
        "isTransparent": false,
        "largeChartUrl": "",
        "displayMode": "{display_mode}",
        "width": "{width}",
        "height": "{height}",
        "colorTheme": "{color_theme}",
        "symbol": "{symbol}",
        "locale": "en"
      }}
      </script>
    </div>
    <!-- TradingView Widget END -->
    """
    
    components.html(widget_html, height=height + 20)


def render_symbol_info(
    symbol: str,
    width: str = "100%",
    color_theme: str = "light",
) -> None:
    """
    Render a TradingView Symbol Info widget.
    
    Compact single-line display of symbol price and change.
    Good for: Inline price display, minimal footprint.
    
    Args:
        symbol: Stock symbol (e.g., "AAPL" or "NASDAQ:AAPL")
        width: Widget width (CSS value)
        color_theme: "light" or "dark"
    """
    if ":" not in symbol:
        symbol = f"NASDAQ:{symbol}"
    
    widget_html = f"""
    <!-- TradingView Widget BEGIN -->
    <div class="tradingview-widget-container">
      <div class="tradingview-widget-container__widget"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-symbol-info.js" async>
      {{
        "symbol": "{symbol}",
        "width": "{width}",
        "locale": "en",
        "colorTheme": "{color_theme}",
        "isTransparent": false
      }}
      </script>
    </div>
    <!-- TradingView Widget END -->
    """
    
    components.html(widget_html, height=80)


def render_company_profile(
    symbol: str,
    width: str = "100%",
    height: int = 550,
    color_theme: str = "light",
) -> None:
    """
    Render a TradingView Company Profile widget.
    
    Shows company description, sector, employees, etc.
    Good for: Company overview section.
    
    Args:
        symbol: Stock symbol (e.g., "AAPL" or "NASDAQ:AAPL")
        width: Widget width (CSS value)
        height: Widget height in pixels
        color_theme: "light" or "dark"
    """
    if ":" not in symbol:
        symbol = f"NASDAQ:{symbol}"
    
    widget_html = f"""
    <!-- TradingView Widget BEGIN -->
    <div class="tradingview-widget-container">
      <div class="tradingview-widget-container__widget"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-symbol-profile.js" async>
      {{
        "width": "{width}",
        "height": "{height}",
        "isTransparent": false,
        "colorTheme": "{color_theme}",
        "symbol": "{symbol}",
        "locale": "en"
      }}
      </script>
    </div>
    <!-- TradingView Widget END -->
    """
    
    components.html(widget_html, height=height + 20)


def render_market_overview(
    width: str = "100%",
    height: int = 660,
    color_theme: str = "light",
    show_chart: bool = True,
    tabs: list = None,
) -> None:
    """
    Render a TradingView Market Overview widget.
    
    Shows multiple markets with tabs (indices, forex, crypto, etc.)
    Good for: Market dashboard, overview page.
    
    Args:
        width: Widget width (CSS value)
        height: Widget height in pixels
        color_theme: "light" or "dark"
        show_chart: Show chart alongside list
        tabs: List of tabs to show
    """
    if tabs is None:
        tabs = [
            {"title": "Indices", "symbols": [
                {"s": "FOREXCOM:SPXUSD", "d": "S&P 500"},
                {"s": "FOREXCOM:NSXUSD", "d": "Nasdaq 100"},
                {"s": "FOREXCOM:DJI", "d": "Dow 30"},
            ]},
            {"title": "Commodities", "symbols": [
                {"s": "CME_MINI:ES1!", "d": "E-Mini S&P"},
                {"s": "CME:GC1!", "d": "Gold"},
                {"s": "NYMEX:CL1!", "d": "Crude Oil"},
            ]},
        ]
    
    tabs_json = str(tabs).replace("'", '"')
    
    widget_html = f"""
    <!-- TradingView Widget BEGIN -->
    <div class="tradingview-widget-container">
      <div class="tradingview-widget-container__widget"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-market-overview.js" async>
      {{
        "colorTheme": "{color_theme}",
        "dateRange": "12M",
        "showChart": {str(show_chart).lower()},
        "locale": "en",
        "width": "{width}",
        "height": "{height}",
        "largeChartUrl": "",
        "isTransparent": false,
        "showSymbolLogo": true,
        "showFloatingTooltip": true,
        "plotLineColorGrowing": "rgba(41, 98, 255, 1)",
        "plotLineColorFalling": "rgba(41, 98, 255, 1)",
        "gridLineColor": "rgba(240, 243, 250, 0)",
        "scaleFontColor": "rgba(106, 109, 120, 1)",
        "belowLineFillColorGrowing": "rgba(41, 98, 255, 0.12)",
        "belowLineFillColorFalling": "rgba(41, 98, 255, 0.12)",
        "belowLineFillColorGrowingBottom": "rgba(41, 98, 255, 0)",
        "belowLineFillColorFallingBottom": "rgba(41, 98, 255, 0)",
        "symbolActiveColor": "rgba(41, 98, 255, 0.12)",
        "tabs": {tabs_json}
      }}
      </script>
    </div>
    <!-- TradingView Widget END -->
    """
    
    components.html(widget_html, height=height + 20)


def render_screener(
    width: str = "100%",
    height: int = 523,
    color_theme: str = "light",
    market: str = "america",
    show_toolbar: bool = True,
    default_screen: str = "most_capitalized",
) -> None:
    """
    Render a TradingView Screener widget.
    
    Interactive stock screener with filters.
    Good for: Stock discovery, screening tools.
    
    Args:
        width: Widget width (CSS value)
        height: Widget height in pixels
        color_theme: "light" or "dark"
        market: Market to screen - "america", "uk", "germany", etc.
        show_toolbar: Show filter toolbar
        default_screen: Default screen to show
                       Options: "most_capitalized", "volume_leaders", 
                               "top_gainers", "top_losers", etc.
    """
    widget_html = f"""
    <!-- TradingView Widget BEGIN -->
    <div class="tradingview-widget-container">
      <div class="tradingview-widget-container__widget"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-screener.js" async>
      {{
        "width": "{width}",
        "height": "{height}",
        "defaultColumn": "overview",
        "defaultScreen": "{default_screen}",
        "market": "{market}",
        "showToolbar": {str(show_toolbar).lower()},
        "colorTheme": "{color_theme}",
        "locale": "en"
      }}
      </script>
    </div>
    <!-- TradingView Widget END -->
    """
    
    components.html(widget_html, height=height + 20)


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_exchange_prefix(symbol: str, default_exchange: str = "NASDAQ") -> str:
    """
    Add exchange prefix to symbol if not present.
    
    Common exchanges:
        - NASDAQ: Tech stocks (AAPL, MSFT, GOOGL)
        - NYSE: Traditional stocks (JPM, GS, WMT)
        - AMEX: Smaller companies, ETFs
    
    Args:
        symbol: Stock symbol
        default_exchange: Default exchange to use
        
    Returns:
        Symbol with exchange prefix (e.g., "NASDAQ:AAPL")
    """
    if ":" in symbol:
        return symbol
    return f"{default_exchange}:{symbol}"


def detect_exchange(symbol: str) -> str:
    """
    Attempt to detect the correct exchange for a symbol.
    
    This is a simple heuristic - for production use,
    you'd want to query an API.
    
    Args:
        symbol: Stock symbol
        
    Returns:
        Exchange prefix string
    """
    # Common NASDAQ stocks
    nasdaq_stocks = {
        "AAPL", "MSFT", "GOOGL", "GOOG", "AMZN", "META", "NVDA", 
        "TSLA", "AVGO", "COST", "PEP", "ADBE", "CSCO", "NFLX",
        "AMD", "INTC", "QCOM", "TXN", "INTU", "AMGN", "SBUX",
    }
    
    # Common NYSE stocks
    nyse_stocks = {
        "JPM", "JNJ", "V", "WMT", "PG", "UNH", "HD", "MA", "BAC",
        "DIS", "VZ", "KO", "MRK", "PFE", "ABT", "CVX", "XOM",
        "GS", "MS", "C", "WFC", "AXP", "IBM", "GE", "CAT",
    }
    
    symbol_upper = symbol.upper()
    
    if symbol_upper in nasdaq_stocks:
        return "NASDAQ"
    elif symbol_upper in nyse_stocks:
        return "NYSE"
    else:
        return "NASDAQ"  # Default to NASDAQ


# =============================================================================
# EXAMPLE USAGE
# =============================================================================

if __name__ == "__main__":
    # This is for testing - run with: streamlit run tradingview_widgets.py
    
    st.set_page_config(layout="wide", page_title="TradingView Widgets Demo")
    st.title("TradingView Widgets Demo")
    
    symbol = st.text_input("Enter Symbol:", value="AAPL")
    
    st.subheader("1. Symbol Overview")
    render_symbol_overview(symbol)
    
    st.subheader("2. Advanced Chart")
    render_advanced_chart(symbol, height=400)
    
    st.subheader("3. Technical Analysis Gauge")
    render_technical_analysis(symbol, height=400)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("4. Mini Chart")
        render_mini_chart(symbol)
    
    with col2:
        st.subheader("5. Symbol Info")
        render_symbol_info(symbol)
    
    st.subheader("6. Fundamental Data")
    render_fundamental_data(symbol, height=500)
