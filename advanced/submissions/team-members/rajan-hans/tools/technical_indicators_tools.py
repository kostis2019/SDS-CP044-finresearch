# tools/technical_indicators_tools.py
# Compute core technical indicators for stocks
# Phase 1 Enhanced: Added Bollinger Bands, ATR, Stochastic, 52-Week Position
# ---------------------------------------------


import pandas as pd
import numpy as np


class TechnicalIndicatorError(Exception):
    """Raised when technical indicators cannot be computed."""


def compute_technical_indicators(price_df: pd.DataFrame) -> dict:
    """
    Compute core technical indicators for a stock.

    Parameters
    ----------
    price_df : pd.DataFrame
        Must contain columns:
        ['date', 'open', 'high', 'low', 'close', 'volume']

    Returns
    -------
    dict
        {
            # Moving Averages
            sma20, sma50, sma200,
            # RSI
            rsi14,
            # MACD
            macd, macd_signal, macd_hist,
            # Volatility
            volatility_30d,
            max_drawdown_1y,
            # Bollinger Bands (NEW)
            bb_upper, bb_middle, bb_lower, bb_width, bb_percent,
            # ATR (NEW)
            atr14, atr_percent,
            # Stochastic Oscillator (NEW)
            stoch_k, stoch_d,
            # 52-Week Position (NEW)
            week_52_high, week_52_low, week_52_position,
            # Labels
            trend_label,
            momentum_label,
            volatility_label (NEW),
            bb_signal (NEW)
        }
    """

    required_cols = {"date", "open", "high", "low", "close", "volume"}
    if not required_cols.issubset(price_df.columns):
        raise TechnicalIndicatorError(
            f"Missing required columns. Found {price_df.columns}"
        )

    if price_df.shape[0] < 200:
        raise TechnicalIndicatorError(
            "At least 200 rows of price data are required to compute indicators."
        )

    df = price_df.copy()
    close = df["close"]
    high = df["high"]
    low = df["low"]

    # -----------------------------
    # SIMPLE MOVING AVERAGES
    # -----------------------------
    df["sma20"] = close.rolling(window=20).mean()
    df["sma50"] = close.rolling(window=50).mean()
    df["sma200"] = close.rolling(window=200).mean()

    sma20 = float(df["sma20"].iloc[-1])
    sma50 = float(df["sma50"].iloc[-1])
    sma200 = float(df["sma200"].iloc[-1])

    # -----------------------------
    # RSI (14)
    # -----------------------------
    delta = close.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    rsi14 = float(rsi.iloc[-1])

    # -----------------------------
    # MACD (12, 26, 9)
    # -----------------------------
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()

    macd_line = ema12 - ema26
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    macd_hist = macd_line - signal_line

    macd = float(macd_line.iloc[-1])
    macd_signal = float(signal_line.iloc[-1])
    macd_hist_val = float(macd_hist.iloc[-1])

    # -----------------------------
    # VOLATILITY (30D ANNUALIZED)
    # -----------------------------
    returns = close.pct_change()
    volatility_30d = float(returns.rolling(window=30).std().iloc[-1] * np.sqrt(252))

    # -----------------------------
    # MAX DRAWDOWN (1Y)
    # -----------------------------
    rolling_max = close.cummax()
    drawdown = (close - rolling_max) / rolling_max
    max_drawdown_1y = float(drawdown.min())

    # -----------------------------
    # BOLLINGER BANDS (20, 2) - NEW
    # -----------------------------
    bb_middle = df["sma20"].iloc[-1]
    bb_std = close.rolling(window=20).std().iloc[-1]
    bb_upper = float(bb_middle + 2 * bb_std)
    bb_lower = float(bb_middle - 2 * bb_std)
    bb_middle = float(bb_middle)
    
    # Bollinger Band Width (volatility indicator)
    bb_width = float((bb_upper - bb_lower) / bb_middle) if bb_middle > 0 else 0
    
    # Bollinger %B (position within bands: 0 = lower, 1 = upper)
    last_close = float(close.iloc[-1])
    bb_percent = float((last_close - bb_lower) / (bb_upper - bb_lower)) if (bb_upper - bb_lower) > 0 else 0.5

    # -----------------------------
    # ATR (14) - NEW
    # Average True Range for volatility
    # -----------------------------
    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = true_range.rolling(window=14).mean()
    atr14 = float(atr.iloc[-1])
    
    # ATR as percentage of price
    atr_percent = float(atr14 / last_close * 100) if last_close > 0 else 0

    # -----------------------------
    # STOCHASTIC OSCILLATOR (14, 3, 3) - NEW
    # -----------------------------
    lowest_low = low.rolling(window=14).min()
    highest_high = high.rolling(window=14).max()
    
    stoch_k_raw = 100 * (close - lowest_low) / (highest_high - lowest_low)
    stoch_k = float(stoch_k_raw.rolling(window=3).mean().iloc[-1])  # %K smoothed
    stoch_d = float(stoch_k_raw.rolling(window=3).mean().rolling(window=3).mean().iloc[-1])  # %D

    # -----------------------------
    # 52-WEEK POSITION - NEW
    # -----------------------------
    # Use last 252 trading days (approximately 1 year)
    year_data = close.tail(252)
    week_52_high = float(year_data.max())
    week_52_low = float(year_data.min())
    
    # Position within 52-week range (0% = at low, 100% = at high)
    week_52_range = week_52_high - week_52_low
    week_52_position = float((last_close - week_52_low) / week_52_range * 100) if week_52_range > 0 else 50

    # -----------------------------
    # TREND LABEL
    # -----------------------------
    if last_close > sma200 * 1.02:
        trend_label = "uptrend"
    elif last_close < sma200 * 0.98:
        trend_label = "downtrend"
    else:
        trend_label = "sideways"

    # -----------------------------
    # MOMENTUM LABEL
    # -----------------------------
    if rsi14 >= 60 and macd > macd_signal:
        momentum_label = "bullish"
    elif rsi14 <= 40 and macd < macd_signal:
        momentum_label = "bearish"
    else:
        momentum_label = "neutral"

    # -----------------------------
    # VOLATILITY LABEL - NEW
    # Based on ATR and BB Width
    # -----------------------------
    if atr_percent > 3 or bb_width > 0.15:
        volatility_label = "high"
    elif atr_percent < 1.5 and bb_width < 0.08:
        volatility_label = "low"
    else:
        volatility_label = "moderate"

    # -----------------------------
    # BOLLINGER BAND SIGNAL - NEW
    # -----------------------------
    if bb_percent > 1:
        bb_signal = "overbought"
    elif bb_percent < 0:
        bb_signal = "oversold"
    elif bb_width < 0.06:
        bb_signal = "squeeze"  # Low volatility, potential breakout
    else:
        bb_signal = "neutral"

    return {
        # Moving Averages
        "sma20": round(sma20, 2),
        "sma50": round(sma50, 2),
        "sma200": round(sma200, 2),
        # RSI
        "rsi14": round(rsi14, 2),
        # MACD
        "macd": round(macd, 4),
        "macd_signal": round(macd_signal, 4),
        "macd_hist": round(macd_hist_val, 4),
        # Volatility
        "volatility_30d": round(volatility_30d, 4),
        "max_drawdown_1y": round(max_drawdown_1y, 4),
        # Bollinger Bands (NEW)
        "bb_upper": round(bb_upper, 2),
        "bb_middle": round(bb_middle, 2),
        "bb_lower": round(bb_lower, 2),
        "bb_width": round(bb_width, 4),
        "bb_percent": round(bb_percent, 4),
        # ATR (NEW)
        "atr14": round(atr14, 4),
        "atr_percent": round(atr_percent, 2),
        # Stochastic (NEW)
        "stoch_k": round(stoch_k, 2),
        "stoch_d": round(stoch_d, 2),
        # 52-Week Position (NEW)
        "week_52_high": round(week_52_high, 2),
        "week_52_low": round(week_52_low, 2),
        "week_52_position": round(week_52_position, 2),
        # Labels
        "trend_label": trend_label,
        "momentum_label": momentum_label,
        "volatility_label": volatility_label,  # NEW
        "bb_signal": bb_signal,  # NEW
    }
