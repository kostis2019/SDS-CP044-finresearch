# charts.py
# Professional chart visualizations for FinResearch AI
# Uses Plotly for interactive charts in Streamlit
# ---------------------------------------------

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, Any, Optional, List


def create_score_radar_chart(scores: Dict[str, float], ticker: str) -> go.Figure:
    """
    Create a radar/spider chart showing all 5 factor scores.
    
    Args:
        scores: Dict with valuation_score, growth_score, profitability_score, 
                financial_health_score, technical_score
        ticker: Stock ticker symbol
    
    Returns:
        Plotly figure object
    """
    categories = ['Valuation', 'Growth', 'Profitability', 'Financial Health', 'Technical']
    
    values = [
        scores.get('valuation_score', 50),
        scores.get('growth_score', 50),
        scores.get('profitability_score', 50),
        scores.get('financial_health_score', 50),
        scores.get('technical_score', 50),
    ]
    
    # Close the radar chart by repeating the first value
    values_closed = values + [values[0]]
    categories_closed = categories + [categories[0]]
    
    fig = go.Figure()
    
    # Add the score trace
    fig.add_trace(go.Scatterpolar(
        r=values_closed,
        theta=categories_closed,
        fill='toself',
        fillcolor='rgba(67, 147, 195, 0.3)',
        line=dict(color='rgb(67, 147, 195)', width=2),
        name=ticker
    ))
    
    # Add a reference line at 50 (neutral)
    fig.add_trace(go.Scatterpolar(
        r=[50] * 6,
        theta=categories_closed,
        fill=None,
        line=dict(color='rgba(128, 128, 128, 0.5)', width=1, dash='dash'),
        name='Neutral (50)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickvals=[0, 25, 50, 75, 100],
                ticktext=['0', '25', '50', '75', '100']
            )
        ),
        showlegend=True,
        title=dict(
            text=f"{ticker} Factor Score Analysis",
            x=0.5,
            font=dict(size=16)
        ),
        height=450,
        margin=dict(l=80, r=80, t=80, b=40)
    )
    
    return fig


def create_score_gauge_chart(score: float, title: str, color_thresholds: bool = True) -> go.Figure:
    """
    Create a gauge chart for a single score.
    
    Args:
        score: Score value (0-100)
        title: Title for the gauge
        color_thresholds: Whether to use color bands
    
    Returns:
        Plotly figure object
    """
    if color_thresholds:
        steps = [
            {'range': [0, 30], 'color': "rgba(255, 99, 71, 0.6)"},      # Red - Sell
            {'range': [30, 45], 'color': "rgba(255, 165, 0, 0.6)"},     # Orange - Reduce
            {'range': [45, 65], 'color': "rgba(255, 255, 0, 0.6)"},     # Yellow - Hold
            {'range': [65, 80], 'color': "rgba(144, 238, 144, 0.6)"},   # Light Green - Buy
            {'range': [80, 100], 'color': "rgba(34, 139, 34, 0.6)"},    # Green - STRONG BUY
        ]
    else:
        steps = [{'range': [0, 100], 'color': "rgba(200, 200, 200, 0.3)"}]
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 14}},
        number={'font': {'size': 24}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1},
            'bar': {'color': "rgb(67, 147, 195)"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': steps,
            'threshold': {
                'line': {'color': "black", 'width': 2},
                'thickness': 0.75,
                'value': score
            }
        }
    ))
    
    fig.update_layout(
        height=200,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    return fig


def create_score_gauges_row(scores: Dict[str, float]) -> go.Figure:
    """
    Create a row of gauge charts for all scores.
    
    Args:
        scores: Dict with all score values
    
    Returns:
        Plotly figure object with subplots
    """
    fig = make_subplots(
        rows=1, cols=5,
        specs=[[{'type': 'indicator'}] * 5],
        subplot_titles=['Valuation', 'Growth', 'Profitability', 'Health', 'Technical']
    )
    
    score_keys = [
        ('valuation_score', 'Valuation'),
        ('growth_score', 'Growth'),
        ('profitability_score', 'Profitability'),
        ('financial_health_score', 'Health'),
        ('technical_score', 'Technical')
    ]
    
    for i, (key, name) in enumerate(score_keys, 1):
        score = scores.get(key, 50)
        
        # Determine color based on score
        if score >= 80:
            bar_color = "rgb(34, 139, 34)"  # Green
        elif score >= 65:
            bar_color = "rgb(144, 238, 144)"  # Light Green
        elif score >= 45:
            bar_color = "rgb(255, 215, 0)"  # Gold
        elif score >= 30:
            bar_color = "rgb(255, 165, 0)"  # Orange
        else:
            bar_color = "rgb(255, 99, 71)"  # Red
        
        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=score,
                gauge={
                    'axis': {'range': [0, 100], 'visible': False},
                    'bar': {'color': bar_color, 'thickness': 0.8},
                    'bgcolor': "rgba(200, 200, 200, 0.3)",
                    'borderwidth': 0,
                },
                number={'font': {'size': 20}},
            ),
            row=1, col=i
        )
    
    fig.update_layout(
        height=180,
        margin=dict(l=20, r=20, t=40, b=20),
        showlegend=False
    )
    
    return fig


def create_sector_comparison_chart(
    stock_metrics: Dict[str, float],
    sector_benchmarks: Dict[str, float],
    ticker: str,
    sector: str
) -> go.Figure:
    """
    Create a bar chart comparing stock metrics to sector benchmarks.
    
    Args:
        stock_metrics: Dict with stock's metrics
        sector_benchmarks: Dict with sector median values
        ticker: Stock ticker
        sector: Sector name
    
    Returns:
        Plotly figure object
    """
    # Define metrics to compare
    metrics = []
    stock_values = []
    sector_values = []
    
    # P/E Ratio
    pe = stock_metrics.get('pe_ttm') or stock_metrics.get('pe')
    sector_pe = sector_benchmarks.get('pe_median')
    if pe and sector_pe:
        metrics.append('P/E Ratio')
        stock_values.append(pe)
        sector_values.append(sector_pe)
    
    # PEG Ratio
    peg = stock_metrics.get('peg_ratio')
    sector_peg = sector_benchmarks.get('peg_median')
    if peg and sector_peg:
        metrics.append('PEG Ratio')
        stock_values.append(peg)
        sector_values.append(sector_peg)
    
    # Operating Margin (convert to percentage)
    op_margin = stock_metrics.get('operating_margin')
    sector_op_margin = sector_benchmarks.get('operating_margin_median')
    if op_margin is not None and sector_op_margin is not None:
        metrics.append('Op. Margin %')
        stock_values.append(op_margin * 100 if op_margin < 1 else op_margin)
        sector_values.append(sector_op_margin * 100 if sector_op_margin < 1 else sector_op_margin)
    
    # ROE (convert to percentage)
    roe = stock_metrics.get('roe')
    sector_roe = sector_benchmarks.get('roe_median', 0.15)  # Default if not available
    if roe is not None:
        metrics.append('ROE %')
        stock_values.append(roe * 100 if roe < 1 else roe)
        sector_values.append(sector_roe * 100 if sector_roe < 1 else sector_roe)
    
    if not metrics:
        return None
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name=ticker,
        x=metrics,
        y=stock_values,
        marker_color='rgb(67, 147, 195)',
        text=[f'{v:.1f}' for v in stock_values],
        textposition='outside'
    ))
    
    fig.add_trace(go.Bar(
        name=f'{sector} Median',
        x=metrics,
        y=sector_values,
        marker_color='rgba(128, 128, 128, 0.6)',
        text=[f'{v:.1f}' for v in sector_values],
        textposition='outside'
    ))
    
    fig.update_layout(
        title=dict(
            text=f"{ticker} vs {sector} Sector",
            x=0.5,
            font=dict(size=16)
        ),
        barmode='group',
        height=350,
        margin=dict(l=40, r=40, t=60, b=40),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        yaxis=dict(title="Value")
    )
    
    return fig


def create_technical_chart(
    technical_indicators: Dict[str, Any],
    ticker: str
) -> go.Figure:
    """
    Create a visual summary of technical indicators.
    
    Args:
        technical_indicators: Dict with RSI, trend, drawdown, etc.
        ticker: Stock ticker
    
    Returns:
        Plotly figure object
    """
    fig = make_subplots(
        rows=1, cols=3,
        specs=[[{'type': 'indicator'}] * 3],
        subplot_titles=['RSI (14)', 'Max Drawdown', 'Volatility']
    )
    
    # RSI Gauge
    rsi = technical_indicators.get('rsi14') or technical_indicators.get('rsi_14') or technical_indicators.get('rsi', 50)
    
    # Determine RSI color
    if rsi > 70:
        rsi_color = "rgb(255, 99, 71)"  # Overbought - Red
    elif rsi < 30:
        rsi_color = "rgb(255, 165, 0)"  # Oversold - Orange
    else:
        rsi_color = "rgb(67, 147, 195)"  # Normal - Blue
    
    fig.add_trace(
        go.Indicator(
            mode="gauge+number",
            value=rsi,
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': rsi_color},
                'steps': [
                    {'range': [0, 30], 'color': "rgba(255, 165, 0, 0.3)"},
                    {'range': [30, 70], 'color': "rgba(200, 200, 200, 0.3)"},
                    {'range': [70, 100], 'color': "rgba(255, 99, 71, 0.3)"},
                ],
                'threshold': {
                    'line': {'color': "black", 'width': 2},
                    'thickness': 0.75,
                    'value': rsi
                }
            },
            number={'suffix': '', 'font': {'size': 20}},
        ),
        row=1, col=1
    )
    
    # Max Drawdown
    drawdown = technical_indicators.get('max_drawdown_1y') or technical_indicators.get('max_drawdown', 0)
    drawdown_pct = abs(drawdown) * 100 if abs(drawdown) < 1 else abs(drawdown)
    
    fig.add_trace(
        go.Indicator(
            mode="number+delta",
            value=drawdown_pct,
            number={'suffix': '%', 'font': {'size': 24, 'color': 'rgb(255, 99, 71)'}},
            delta={'reference': 20, 'relative': False, 'increasing': {'color': 'red'}, 'decreasing': {'color': 'green'}},
        ),
        row=1, col=2
    )
    
    # Volatility
    volatility = technical_indicators.get('volatility_1y') or technical_indicators.get('volatility', 0)
    volatility_pct = volatility * 100 if volatility < 1 else volatility
    
    fig.add_trace(
        go.Indicator(
            mode="number",
            value=volatility_pct,
            number={'suffix': '%', 'font': {'size': 24}},
        ),
        row=1, col=3
    )
    
    fig.update_layout(
        height=200,
        margin=dict(l=20, r=20, t=50, b=20),
        showlegend=False
    )
    
    return fig


def create_final_score_display(
    final_score: float,
    rating: str,
    confidence: str = "MEDIUM"
) -> go.Figure:
    """
    Create a large display for the final score and rating.
    
    Args:
        final_score: Final investment score (0-100)
        rating: Rating string (STRONG BUY, BUY, HOLD, REDUCE, SELL)
        confidence: Confidence level
    
    Returns:
        Plotly figure object
    """
    # Determine color based on rating
    rating_colors = {
        "STRONG BUY": "rgb(34, 139, 34)",
        "BUY": "rgb(144, 238, 144)",
        "HOLD": "rgb(255, 215, 0)",
        "REDUCE": "rgb(255, 165, 0)",
        "SELL": "rgb(255, 99, 71)",
    }
    
    color = rating_colors.get(rating.upper(), "rgb(128, 128, 128)")
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=final_score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': f"<b>{rating}</b><br><span style='font-size:12px'>Confidence: {confidence}</span>", 
               'font': {'size': 18}},
        number={'font': {'size': 48}, 'suffix': ''},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkgray"},
            'bar': {'color': color, 'thickness': 0.75},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 30], 'color': "rgba(255, 99, 71, 0.2)"},
                {'range': [30, 45], 'color': "rgba(255, 165, 0, 0.2)"},
                {'range': [45, 65], 'color': "rgba(255, 255, 0, 0.2)"},
                {'range': [65, 80], 'color': "rgba(144, 238, 144, 0.2)"},
                {'range': [80, 100], 'color': "rgba(34, 139, 34, 0.2)"},
            ],
        }
    ))
    
    fig.update_layout(
        height=280,
        margin=dict(l=30, r=30, t=60, b=30)
    )
    
    return fig


def create_price_chart(
    price_data: pd.DataFrame,
    ticker: str,
    show_ma: bool = True
) -> go.Figure:
    """
    Create a candlestick or line chart with optional moving averages.
    
    Args:
        price_data: DataFrame with date, open, high, low, close, volume
        ticker: Stock ticker
        show_ma: Whether to show moving averages
    
    Returns:
        Plotly figure object
    """
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.75, 0.25],
        subplot_titles=[f'{ticker} Price', 'Volume']
    )
    
    # Price line
    fig.add_trace(
        go.Scatter(
            x=price_data['date'],
            y=price_data['close'],
            mode='lines',
            name='Close',
            line=dict(color='rgb(67, 147, 195)', width=2)
        ),
        row=1, col=1
    )
    
    # Moving averages
    if show_ma and len(price_data) >= 50:
        # 20-day MA
        price_data['ma20'] = price_data['close'].rolling(window=20).mean()
        fig.add_trace(
            go.Scatter(
                x=price_data['date'],
                y=price_data['ma20'],
                mode='lines',
                name='20-day MA',
                line=dict(color='orange', width=1, dash='dash')
            ),
            row=1, col=1
        )
        
        # 50-day MA
        price_data['ma50'] = price_data['close'].rolling(window=50).mean()
        fig.add_trace(
            go.Scatter(
                x=price_data['date'],
                y=price_data['ma50'],
                mode='lines',
                name='50-day MA',
                line=dict(color='green', width=1, dash='dash')
            ),
            row=1, col=1
        )
    
    # Volume
    colors = ['red' if price_data['close'].iloc[i] < price_data['open'].iloc[i] 
              else 'green' for i in range(len(price_data))]
    
    fig.add_trace(
        go.Bar(
            x=price_data['date'],
            y=price_data['volume'],
            name='Volume',
            marker_color=colors,
            opacity=0.5
        ),
        row=2, col=1
    )
    
    fig.update_layout(
        height=450,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=40, r=40, t=60, b=40),
        xaxis_rangeslider_visible=False
    )
    
    fig.update_yaxes(title_text="Price ($)", row=1, col=1)
    fig.update_yaxes(title_text="Volume", row=2, col=1)
    
    return fig
