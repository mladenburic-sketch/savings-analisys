"""
Module for creating visualizations for disputes analysis
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Optional


def plot_discrepancy_timeline(df: pd.DataFrame, date_col: str = 'disputedAt') -> go.Figure:
    """
    Plots line chart showing savings (positive) and underbilled (negative) over time.
    
    Args:
        df: DataFrame with data
        date_col: Column name with date
        
    Returns:
        Plotly Figure
    """
    df_copy = df.copy()
    df_copy[date_col] = pd.to_datetime(df_copy[date_col])
    df_copy = df_copy.sort_values(date_col)
    
    # Separate positive (savings) and negative (underbilled)
    df_savings = df_copy[df_copy['discrepancy_value'] > 0].copy()
    df_underbilled = df_copy[df_copy['discrepancy_value'] < 0].copy()
    
    fig = go.Figure()
    
    # Plot savings (positive values) in green
    if not df_savings.empty:
        fig.add_trace(go.Scatter(
            x=df_savings[date_col],
            y=df_savings['discrepancy_value'],
            mode='markers',
            name='Savings',
            marker=dict(color='#00CC96', size=6, symbol='circle'),
            hovertemplate='<b>Date:</b> %{x}<br>' +
                          '<b>Savings:</b> $%{y:,.2f}<extra></extra>'
        ))
    
    # Plot underbilled (negative values) in red
    if not df_underbilled.empty:
        fig.add_trace(go.Scatter(
            x=df_underbilled[date_col],
            y=df_underbilled['discrepancy_value'],
            mode='markers',
            name='Underbilled',
            marker=dict(color='#EF553B', size=6, symbol='circle'),
            hovertemplate='<b>Date:</b> %{x}<br>' +
                          '<b>Underbilled:</b> $%{y:,.2f}<extra></extra>'
        ))
    
    # Add zero line
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
    
    fig.update_layout(
        title='Savings vs Underbilled Over Time',
        xaxis_title='Date',
        yaxis_title='Value ($) - Green: Savings, Red: Underbilled',
        hovermode='closest',
        height=500,
        margin=dict(t=60, b=60, l=60, r=60),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig


def plot_discrepancy_by_category(df: pd.DataFrame, category_col: str, 
                                 top_n: int = 10) -> go.Figure:
    """
    Plots bar chart showing savings (positive) and underbilled (negative) by category.
    
    Args:
        df: DataFrame with data
        category_col: Column name for category
        top_n: Number of top categories to display
        
    Returns:
        Plotly Figure
    """
    if category_col not in df.columns:
        return go.Figure()
    
    grouped = df.groupby(category_col)['discrepancy_value'].sum().reset_index()
    
    # Sort by absolute value to show most impactful categories
    grouped['abs_value'] = grouped['discrepancy_value'].abs()
    grouped = grouped.sort_values('abs_value', ascending=False).head(top_n)
    grouped = grouped.sort_values('discrepancy_value', ascending=False)
    
    fig = go.Figure()
    
    # Green for savings (positive), red for underbilled (negative)
    colors = ['#00CC96' if x > 0 else '#EF553B' for x in grouped['discrepancy_value']]
    
    # Create labels
    labels = []
    for val in grouped['discrepancy_value']:
        if val > 0:
            labels.append(f'Savings: ${val:,.2f}')
        else:
            labels.append(f'Underbilled: ${abs(val):,.2f}')
    
    fig.add_trace(go.Bar(
        x=grouped[category_col],
        y=grouped['discrepancy_value'],
        marker_color=colors,
        text=labels,
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>' +
                      '<b>Value:</b> $%{y:,.2f}<br>' +
                      '<b>Type:</b> %{customdata}<extra></extra>',
        customdata=['Savings' if x > 0 else 'Underbilled' for x in grouped['discrepancy_value']]
    ))
    
    # Add zero line
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
    
    fig.update_layout(
        title=f'Savings vs Underbilled by {category_col}',
        xaxis_title=category_col,
        yaxis_title='Value ($) - Green: Savings, Red: Underbilled',
        height=500,
        margin=dict(t=60, b=60, l=60, r=60),
        xaxis=dict(tickangle=-45)
    )
    
    return fig


def plot_discrepancy_distribution(df: pd.DataFrame) -> go.Figure:
    """
    Plots histogram showing distribution of savings (positive) and underbilled (negative).
    
    Args:
        df: DataFrame with data
        
    Returns:
        Plotly Figure
    """
    fig = go.Figure()
    
    # Separate positive and negative values
    savings = df[df['discrepancy_value'] > 0]['discrepancy_value']
    underbilled = df[df['discrepancy_value'] < 0]['discrepancy_value']
    
    # Plot savings in green
    if not savings.empty:
        fig.add_trace(go.Histogram(
            x=savings,
            nbinsx=30,
            name='Savings',
            marker_color='#00CC96',
            opacity=0.7,
            hovertemplate='<b>Range:</b> $%{x}<br>' +
                          '<b>Count:</b> %{y}<br>' +
                          '<b>Type:</b> Savings<extra></extra>'
        ))
    
    # Plot underbilled in red
    if not underbilled.empty:
        fig.add_trace(go.Histogram(
            x=underbilled,
            nbinsx=30,
            name='Underbilled',
            marker_color='#EF553B',
            opacity=0.7,
            hovertemplate='<b>Range:</b> $%{x}<br>' +
                          '<b>Count:</b> %{y}<br>' +
                          '<b>Type:</b> Underbilled<extra></extra>'
        ))
    
    # Add zero line
    fig.add_vline(x=0, line_dash="dash", line_color="gray", opacity=0.5)
    
    fig.update_layout(
        title='Distribution of Savings vs Underbilled',
        xaxis_title='Value ($) - Green: Savings, Red: Underbilled',
        yaxis_title='Count',
        height=500,
        margin=dict(t=60, b=60, l=60, r=60),
        barmode='overlay',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig


def plot_discrepancy_pie(df: pd.DataFrame, category_col: str) -> go.Figure:
    """
    Plots pie chart showing savings vs underbilled distribution by category.
    
    Args:
        df: DataFrame with data
        category_col: Column name for category
        
    Returns:
        Plotly Figure
    """
    if category_col not in df.columns:
        return go.Figure()
    
    grouped = df.groupby(category_col)['discrepancy_value'].sum().reset_index()
    grouped = grouped[grouped['discrepancy_value'] != 0]  # Remove zeros
    
    # Create labels with savings/underbilled indication
    labels = []
    for idx, row in grouped.iterrows():
        if row['discrepancy_value'] > 0:
            labels.append(f"{row[category_col]}<br>(Savings: ${row['discrepancy_value']:,.2f})")
        else:
            labels.append(f"{row[category_col]}<br>(Underbilled: ${abs(row['discrepancy_value']):,.2f})")
    
    # Colors: green for savings, red for underbilled
    colors = ['#00CC96' if x > 0 else '#EF553B' for x in grouped['discrepancy_value']]
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=grouped['discrepancy_value'].abs(),  # Use absolute values for pie
        hole=0.4,
        marker=dict(colors=colors),
        textinfo='label+percent',
        texttemplate='%{label}<br>%{percent}',
        customdata=grouped['discrepancy_value'],
        hovertemplate='<b>%{label}</b><br>Value: $%{customdata:,.2f}<br>%{percent}<extra></extra>'
    )])
    
    fig.update_layout(
        title=f'Savings vs Underbilled Distribution by {category_col}',
        height=600,
        margin=dict(t=60, b=60, l=60, r=60)
    )
    
    return fig


def plot_daily_summary(df: pd.DataFrame, date_col: str = 'disputedAt') -> go.Figure:
    """
    Plots chart with daily sum showing savings vs underbilled and number of disputes.
    
    Args:
        df: DataFrame with data
        date_col: Column name with date
        
    Returns:
        Plotly Figure with subplots
    """
    from plotly.subplots import make_subplots
    
    df_copy = df.copy()
    df_copy[date_col] = pd.to_datetime(df_copy[date_col])
    df_copy = df_copy.set_index(date_col)
    
    # Calculate daily totals for savings and underbilled separately
    daily_savings = df_copy[df_copy['discrepancy_value'] > 0].resample('D')['discrepancy_value'].sum()
    daily_underbilled = df_copy[df_copy['discrepancy_value'] < 0].resample('D')['discrepancy_value'].sum()
    daily_total = df_copy.resample('D')['discrepancy_value'].sum()
    daily_count = df_copy.resample('D')['po_number'].count()
    
    # Combine into single dataframe
    daily = pd.DataFrame({
        date_col: daily_total.index,
        'savings': daily_savings.reindex(daily_total.index, fill_value=0),
        'underbilled': daily_underbilled.reindex(daily_total.index, fill_value=0),
        'total': daily_total.values,
        'count': daily_count.values
    })
    
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Daily Savings vs Underbilled', 'Number of Disputes per Day'),
        vertical_spacing=0.15,
        row_heights=[0.6, 0.4]
    )
    
    # First chart - savings and underbilled as separate bars
    fig.add_trace(
        go.Bar(
            x=daily[date_col],
            y=daily['savings'],
            name='Savings',
            marker_color='#00CC96',
            hovertemplate='<b>Date:</b> %{x}<br><b>Savings:</b> $%{y:,.2f}<extra></extra>'
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Bar(
            x=daily[date_col],
            y=daily['underbilled'],
            name='Underbilled',
            marker_color='#EF553B',
            hovertemplate='<b>Date:</b> %{x}<br><b>Underbilled:</b> $%{y:,.2f}<extra></extra>'
        ),
        row=1, col=1
    )
    
    # Add zero line
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5, row=1, col=1)
    
    # Second chart - dispute count
    fig.add_trace(
        go.Bar(
            x=daily[date_col],
            y=daily['count'],
            name='Dispute Count',
            marker_color='#636EFA',
            showlegend=False,
            hovertemplate='<b>Date:</b> %{x}<br><b>Count:</b> %{y}<extra></extra>'
        ),
        row=2, col=1
    )
    
    fig.update_xaxes(title_text="Date", row=2, col=1)
    fig.update_yaxes(title_text="Value ($)", row=1, col=1)
    fig.update_yaxes(title_text="Count", row=2, col=1)
    
    fig.update_layout(
        height=700,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=60, b=60, l=60, r=60)
    )
    
    return fig

