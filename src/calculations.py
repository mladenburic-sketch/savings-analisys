"""
Module for calculations and metrics for disputes analysis
"""

import pandas as pd
from typing import Dict, Optional


def calculate_summary_metrics(df: pd.DataFrame) -> Dict[str, float]:
    """
    Calculates basic metrics for disputes.
    
    Args:
        df: DataFrame with disputes data
        
    Returns:
        Dictionary with metrics
    """
    metrics = {
        'total_disputes': len(df),
        'total_discrepancy_value': df['discrepancy_value'].sum(),
        'total_gallons': df['gallons'].sum(),
        'avg_discrepancy_per_dispute': df['discrepancy_value'].mean(),
        'avg_gallons_per_dispute': df['gallons'].mean(),
        'total_positive_discrepancy': df[df['discrepancy_value'] > 0]['discrepancy_value'].sum(),
        'total_negative_discrepancy': abs(df[df['discrepancy_value'] < 0]['discrepancy_value'].sum()),
        'disputes_with_positive_value': len(df[df['discrepancy_value'] > 0]),
        'disputes_with_negative_value': len(df[df['discrepancy_value'] < 0]),
    }
    
    return metrics


def calculate_by_category(df: pd.DataFrame, category_col: str) -> pd.DataFrame:
    """
    Calculates aggregated metrics by category.
    
    Args:
        df: DataFrame with data
        category_col: Column name for category
        
    Returns:
        DataFrame with aggregated data
    """
    if category_col not in df.columns:
        return pd.DataFrame()
    
    grouped = df.groupby(category_col).agg({
        'discrepancy_value': ['sum', 'mean', 'count'],
        'gallons': ['sum', 'mean'],
        'expected_rate': 'mean',
        'billed_rate': 'mean',
    }).round(2)
    
    grouped.columns = ['total_discrepancy', 'avg_discrepancy', 'count', 
                      'total_gallons', 'avg_gallons', 'avg_expected_rate', 'avg_billed_rate']
    grouped = grouped.reset_index()
    grouped = grouped.sort_values('total_discrepancy', ascending=False)
    
    return grouped


def calculate_by_date(df: pd.DataFrame, date_col: str = 'disputedAt', 
                     freq: str = 'D') -> pd.DataFrame:
    """
    Calculates aggregated metrics by date.
    
    Args:
        df: DataFrame with data
        date_col: Column name with date
        freq: Aggregation frequency ('D' for day, 'W' for week, 'M' for month)
        
    Returns:
        DataFrame with aggregated data by date
    """
    if date_col not in df.columns:
        return pd.DataFrame()
    
    df_copy = df.copy()
    df_copy[date_col] = pd.to_datetime(df_copy[date_col])
    df_copy = df_copy.set_index(date_col)
    
    grouped = df_copy.resample(freq).agg({
        'discrepancy_value': ['sum', 'count'],
        'gallons': 'sum',
    })
    
    grouped.columns = ['total_discrepancy', 'dispute_count', 'total_gallons']
    grouped = grouped.reset_index()
    
    return grouped


def calculate_top_disputes(df: pd.DataFrame, n: int = 10, 
                          sort_by: str = 'discrepancy_value') -> pd.DataFrame:
    """
    Returns top N disputes by value.
    
    Args:
        df: DataFrame with data
        n: Number of disputes to display
        sort_by: Column for sorting
        
    Returns:
        DataFrame with top N disputes
    """
    if sort_by not in df.columns:
        sort_by = 'discrepancy_value'
    
    top_df = df.nlargest(n, sort_by)[
        ['po_number', 'customerName', 'siteName', 'item', 
         'discrepancy_value', 'gallons', 'disputedAt', 'discrepancy_type']
    ].copy()
    
    return top_df

