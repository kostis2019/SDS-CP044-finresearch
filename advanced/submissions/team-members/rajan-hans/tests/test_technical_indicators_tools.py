# tests/test_technicals_tools.py

import pandas as pd
from tools.price_tools import get_price_history
from tools.technical_indicators_tools import compute_technical_indicators


def test_compute_technical_indicators_basic():
    df = get_price_history("AAPL", period="1y")
    indicators = compute_technical_indicators(df)

    expected_keys = {
        "sma20",
        "sma50",
        "sma200",
        "rsi14",
        "macd",
        "macd_signal",
        "macd_hist",
        "volatility_30d",
        "max_drawdown_1y",
        "trend_label",
        "momentum_label",
    }

    assert set(indicators.keys()) == expected_keys
    assert 0 <= indicators["rsi14"] <= 100
    assert indicators["trend_label"] in ["uptrend", "downtrend", "sideways"]
    assert indicators["momentum_label"] in ["bullish", "bearish", "neutral"]


def test_drawdown_is_negative():
    df = get_price_history("AAPL", period="1y")
    indicators = compute_technical_indicators(df)

    assert indicators["max_drawdown_1y"] <= 0
