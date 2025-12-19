"""
Module for loading and preparing disputes data
"""

import pandas as pd
from pathlib import Path
from datetime import datetime


def load_disputes_data(data_file: str = "data/disputes-all-data.csv") -> pd.DataFrame:
    """
    Loads CSV file with disputes data.
    
    Args:
        data_file: Path to CSV file
        
    Returns:
        DataFrame with disputes data
    """
    file_path = Path(data_file)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {data_file}")
    
    df = pd.read_csv(file_path)
    
    # Convert disputedAt to datetime
    if 'disputedAt' in df.columns:
        df['disputedAt'] = pd.to_datetime(df['disputedAt'], errors='coerce')
    
    # Convert overriddenAt to datetime if exists
    if 'overriddenAt' in df.columns:
        df['overriddenAt'] = pd.to_datetime(df['overriddenAt'], errors='coerce')
    
    # Convert archivedAt to datetime if exists
    if 'archivedAt' in df.columns:
        df['archivedAt'] = pd.to_datetime(df['archivedAt'], errors='coerce')
    
    return df


def clean_disputes_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans and prepares data for analysis.
    
    Args:
        df: Raw DataFrame
        
    Returns:
        Cleaned DataFrame
    """
    df_clean = df.copy()
    
    # Fill empty values for numeric columns with 0
    numeric_cols = ['expected_rate', 'billed_rate', 'difference_per_unit', 
                    'gallons', 'discrepancy_value']
    for col in numeric_cols:
        if col in df_clean.columns:
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce').fillna(0)
    
    # Add date column (date only, without time)
    if 'disputedAt' in df_clean.columns:
        df_clean['disputed_date'] = df_clean['disputedAt'].dt.date
    
    # Add month and year columns
    if 'disputedAt' in df_clean.columns:
        df_clean['disputed_month'] = df_clean['disputedAt'].dt.to_period('M')
        df_clean['disputed_year'] = df_clean['disputedAt'].dt.year
    
    return df_clean

