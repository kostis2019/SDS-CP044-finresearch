# tools/yfinance_provider.py
# Centralized yfinance data provider with caching
# Eliminates redundant API calls across tools
# ---------------------------------------------

import yfinance as yf
import pandas as pd
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import threading


@dataclass
class CachedTickerData:
    """Container for all cached data for a single ticker."""

    ticker: str
    created_at: datetime = field(default_factory=datetime.now)

    # Cached data (None means not yet fetched)
    _yf_ticker: Any = field(default=None, repr=False)
    _info: Optional[Dict] = field(default=None, repr=False)
    _history: Dict[str, pd.DataFrame] = field(
        default_factory=dict, repr=False
    )  # keyed by period
    _financials: Optional[pd.DataFrame] = field(default=None, repr=False)
    _balance_sheet: Optional[pd.DataFrame] = field(default=None, repr=False)
    _cashflow: Optional[pd.DataFrame] = field(default=None, repr=False)
    _recommendations: Optional[pd.DataFrame] = field(default=None, repr=False)
    _insider_transactions: Optional[pd.DataFrame] = field(default=None, repr=False)
    _institutional_holders: Optional[pd.DataFrame] = field(default=None, repr=False)

    def is_expired(self, max_age_minutes: int = 30) -> bool:
        """Check if cache has expired."""
        age = datetime.now() - self.created_at
        return age > timedelta(minutes=max_age_minutes)


class YFinanceProvider:
    """
    Centralized provider for all yfinance data.

    Benefits:
    - Single yf.Ticker() instance per ticker
    - Lazy loading: data fetched only when needed
    - In-memory caching for duration of analysis
    - Thread-safe access
    - Automatic cache expiration

    Usage:
        provider = get_yfinance_provider()
        info = provider.get_info("AAPL")
        history = provider.get_history("AAPL", period="1y")
    """

    def __init__(self, cache_ttl_minutes: int = 30):
        self._cache: Dict[str, CachedTickerData] = {}
        self._lock = threading.Lock()
        self._cache_ttl = cache_ttl_minutes

    def _get_or_create_cache(self, ticker: str) -> CachedTickerData:
        """Get existing cache or create new one for ticker."""
        ticker = ticker.upper()

        with self._lock:
            if ticker in self._cache:
                cached = self._cache[ticker]
                if not cached.is_expired(self._cache_ttl):
                    return cached
                # Expired, remove it
                del self._cache[ticker]

            # Create new cache entry
            cached = CachedTickerData(ticker=ticker)
            cached._yf_ticker = yf.Ticker(ticker)
            self._cache[ticker] = cached
            return cached

    def get_info(self, ticker: str) -> Dict[str, Any]:
        """
        Get ticker info (company profile, ratios, etc.)
        Cached after first call.
        """
        cached = self._get_or_create_cache(ticker)

        if cached._info is None:
            cached._info = cached._yf_ticker.info or {}

        return cached._info

    def get_history(
        self,
        ticker: str,
        period: str = "1y",
        interval: str = "1d",
        auto_adjust: bool = False,
    ) -> pd.DataFrame:
        """
        Get price history DataFrame.
        Cached per period/interval combination.
        """
        cached = self._get_or_create_cache(ticker)
        cache_key = f"{period}_{interval}"

        if cache_key not in cached._history:
            df = cached._yf_ticker.history(
                period=period, interval=interval, auto_adjust=auto_adjust
            )
            cached._history[cache_key] = df

        return cached._history[cache_key]

    def get_financials(self, ticker: str) -> pd.DataFrame:
        """Get income statement (financials). Cached."""
        cached = self._get_or_create_cache(ticker)

        if cached._financials is None:
            cached._financials = cached._yf_ticker.financials

        return cached._financials

    def get_balance_sheet(self, ticker: str) -> pd.DataFrame:
        """Get balance sheet. Cached."""
        cached = self._get_or_create_cache(ticker)

        if cached._balance_sheet is None:
            cached._balance_sheet = cached._yf_ticker.balance_sheet

        return cached._balance_sheet

    def get_cashflow(self, ticker: str) -> pd.DataFrame:
        """Get cash flow statement. Cached."""
        cached = self._get_or_create_cache(ticker)

        if cached._cashflow is None:
            cached._cashflow = cached._yf_ticker.cashflow

        return cached._cashflow

    def get_recommendations(self, ticker: str) -> Optional[pd.DataFrame]:
        """Get analyst recommendations. Cached."""
        cached = self._get_or_create_cache(ticker)

        if cached._recommendations is None:
            cached._recommendations = cached._yf_ticker.recommendations

        return cached._recommendations

    def get_insider_transactions(self, ticker: str) -> Optional[pd.DataFrame]:
        """Get insider transactions. Cached."""
        cached = self._get_or_create_cache(ticker)

        if cached._insider_transactions is None:
            cached._insider_transactions = cached._yf_ticker.insider_transactions

        return cached._insider_transactions

    def get_institutional_holders(self, ticker: str) -> Optional[pd.DataFrame]:
        """Get institutional holders. Cached."""
        cached = self._get_or_create_cache(ticker)

        if cached._institutional_holders is None:
            cached._institutional_holders = cached._yf_ticker.institutional_holders

        return cached._institutional_holders

    def clear_cache(self, ticker: Optional[str] = None):
        """Clear cache for specific ticker or all tickers."""
        with self._lock:
            if ticker:
                self._cache.pop(ticker.upper(), None)
            else:
                self._cache.clear()

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics for debugging."""
        with self._lock:
            return {
                "cached_tickers": list(self._cache.keys()),
                "total_cached": len(self._cache),
                "cache_ttl_minutes": self._cache_ttl,
            }


# Singleton instance
_provider_instance: Optional[YFinanceProvider] = None
_provider_lock = threading.Lock()


def get_yfinance_provider() -> YFinanceProvider:
    """Get the singleton YFinanceProvider instance."""
    global _provider_instance

    with _provider_lock:
        if _provider_instance is None:
            _provider_instance = YFinanceProvider()
        return _provider_instance


def reset_yfinance_provider():
    """Reset the singleton (useful for testing or forcing fresh data)."""
    global _provider_instance

    with _provider_lock:
        if _provider_instance:
            _provider_instance.clear_cache()
        _provider_instance = None
