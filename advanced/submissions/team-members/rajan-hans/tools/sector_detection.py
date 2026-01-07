# tools/sector_detection.py
# Auto-detect sector from ticker using Yahoo Finance
# ---------------------------------------------

# import yfinance as yf
from tools.yfinance_provider import get_yfinance_provider
from typing import Optional, Tuple


# Mapping from Yahoo Finance sector names to our benchmark sector names
SECTOR_MAPPING = {
    # Direct matches (Yahoo Finance name matches our benchmark name)
    "Technology": "Technology",
    "Healthcare": "Healthcare",
    "Financial Services": "Financial Services",
    "Industrials": "Industrials",
    "Energy": "Energy",
    "Utilities": "Utilities",
    "Consumer Cyclical": "Consumer Cyclical",
    "Communication Services": "Communication Services",
    "Basic Materials": "Basic Materials",
    "Real Estate": "Real Estate",
    "Consumer Defensive": "Consumer Defensive",
}

# Default sector if detection fails
DEFAULT_SECTOR = "Technology"


def detect_sector(ticker: str) -> Tuple[str, Optional[str]]:
    """
    Auto-detect the sector for a given ticker using Yahoo Finance.

    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL')

    Returns:
        Tuple of (mapped_sector, raw_sector)
        - mapped_sector: Sector name that matches our benchmarks
        - raw_sector: Original sector name from Yahoo Finance (or None if not found)
    """
    try:
        provider = get_yfinance_provider()
        info = provider.get_info(ticker)

        raw_sector = info.get("sector")

        if not raw_sector:
            return DEFAULT_SECTOR, None

        # Map to our benchmark sectors
        mapped_sector = SECTOR_MAPPING.get(raw_sector, DEFAULT_SECTOR)

        return mapped_sector, raw_sector

    except Exception as e:
        print(f"[Warning] Could not detect sector for {ticker}: {e}")
        return DEFAULT_SECTOR, None


def get_sector_with_fallback(ticker: str, fallback: str = DEFAULT_SECTOR) -> str:
    """
    Get sector for a ticker, with a fallback value if detection fails.

    Args:
        ticker: Stock ticker symbol
        fallback: Fallback sector if detection fails

    Returns:
        Sector name (either detected or fallback)
    """
    mapped_sector, _ = detect_sector(ticker)
    return mapped_sector if mapped_sector else fallback
