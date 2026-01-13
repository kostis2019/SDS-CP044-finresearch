# tools/price_tools.py
# Fetch historical OHLCV price data for a ticker using yfinance
# ---------------------------------------------

from typing import Optional
import pandas as pd

# import yfinance as yf
from tools.yfinance_provider import get_yfinance_provider


class PriceHistoryError(Exception):
    """Raised when price history cannot be retrieved or validated."""


def get_price_history(
    ticker: str, period: str = "1y", interval: str = "1d"
) -> pd.DataFrame:
    """Fetch historical OHLCV price data."""

    if not ticker or not isinstance(ticker, str):
        raise PriceHistoryError("Ticker must be a non-empty string.")

    try:
        provider = get_yfinance_provider()
        df = provider.get_history(ticker, period=period, interval=interval, auto_adjust=False)

    except Exception as e:
        raise PriceHistoryError(f"Failed to fetch price data for {ticker}: {e}")

    if df.empty:
        raise PriceHistoryError(f"No price data returned for {ticker}.")

    # 1. Reset index to ensure Date is a column
    df = df.reset_index()

    # 2. Normalize columns to lowercase for safe matching
    df.columns = [c.lower() for c in df.columns]

    # 3. Handle Date/Datetime naming variations
    if "date" not in df.columns and "datetime" in df.columns:
        df = df.rename(columns={"datetime": "date"})

    if "date" not in df.columns:
        raise PriceHistoryError("Could not identify date column in API response.")

    # 4. Validate required columns
    required_cols = {"open", "high", "low", "close", "volume", "date"}
    if not required_cols.issubset(set(df.columns)):
        raise PriceHistoryError(
            f"Missing required columns for {ticker}. " f"Found: {list(df.columns)}"
        )

    # 5. Clean up types
    df["date"] = pd.to_datetime(df["date"]).dt.tz_localize(None)
    df = df.sort_values("date").reset_index(drop=True)

    if df.shape[0] < 50:
        raise PriceHistoryError(
            f"Insufficient price history for {ticker}. "
            f"Only {df.shape[0]} rows returned."
        )

    return df[["date", "open", "high", "low", "close", "volume"]]
