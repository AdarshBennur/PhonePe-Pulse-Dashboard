"""
Data loading and processing utilities for PhonePe Pulse Dashboard
"""

import pandas as pd
import streamlit as st
import os
from typing import Dict, List, Tuple
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path


# Get the project root directory (parent of utils directory)
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"


def get_data_path(filename: str) -> Path:
    """Get the full path to a data file"""
    return DATA_DIR / filename


@st.cache_data
def load_aggregated_transactions() -> pd.DataFrame:
    """Load and cache aggregated transactions data"""
    try:
        df = pd.read_csv(get_data_path('aggregated_transactions.csv'))
        return df
    except FileNotFoundError:
        st.error("Aggregated transactions data not found!")
        return pd.DataFrame()


@st.cache_data
def load_aggregated_users() -> pd.DataFrame:
    """Load and cache aggregated users data"""
    try:
        df = pd.read_csv(get_data_path('aggregated_users.csv'))
        return df
    except FileNotFoundError:
        st.error("Aggregated users data not found!")
        return pd.DataFrame()


@st.cache_data
def load_aggregated_insurance() -> pd.DataFrame:
    """Load and cache aggregated insurance data"""
    try:
        df = pd.read_csv(get_data_path('aggregated_insurance.csv'))
        return df
    except FileNotFoundError:
        st.error("Aggregated insurance data not found!")
        return pd.DataFrame()


@st.cache_data
def load_map_transactions() -> pd.DataFrame:
    """Load and cache map transactions data"""
    try:
        df = pd.read_csv(get_data_path('map_transactions.csv'))
        return df
    except FileNotFoundError:
        st.error("Map transactions data not found!")
        return pd.DataFrame()


@st.cache_data
def load_top_performers() -> pd.DataFrame:
    """Load and cache top performers data"""
    try:
        df = pd.read_csv(get_data_path('top_performers.csv'))
        return df
    except FileNotFoundError:
        st.error("Top performers data not found!")
        return pd.DataFrame()


@st.cache_data
def get_summary_stats() -> Dict:
    """Calculate and cache summary statistics"""
    trans_df = load_aggregated_transactions()
    users_df = load_aggregated_users()
    insurance_df = load_aggregated_insurance()
    
    if trans_df.empty or users_df.empty or insurance_df.empty:
        return {}
    
    return {
        'total_transactions': trans_df['Transaction_Count'].sum(),
        'total_transaction_amount': trans_df['Transaction_Amount'].sum(),
        'total_users': users_df['Registered_Users'].sum(),
        'total_app_opens': users_df['App_Opens'].sum(),
        'total_insurance_count': insurance_df['Insurance_Count'].sum(),
        'total_insurance_amount': insurance_df['Insurance_Amount'].sum(),
        'unique_states': trans_df['State'].nunique(),
        'years_covered': f"{trans_df['Year'].min()} - {trans_df['Year'].max()}"
    }


def get_state_list() -> List[str]:
    """Get list of unique states"""
    df = load_aggregated_transactions()
    if df.empty:
        return []
    return sorted(df['State'].unique().tolist())


def get_year_list() -> List[int]:
    """Get list of unique years"""
    df = load_aggregated_transactions()
    if df.empty:
        return []
    return sorted(df['Year'].unique().tolist())


def get_quarter_list() -> List[int]:
    """Get list of unique quarters"""
    df = load_aggregated_transactions()
    if df.empty:
        return []
    return sorted(df['Quarter'].unique().tolist())


def format_currency(amount: float) -> str:
    """Format currency in Indian format"""
    if amount >= 1e9:
        return f"₹{amount/1e9:.2f}B"
    elif amount >= 1e7:
        return f"₹{amount/1e7:.2f}Cr"
    elif amount >= 1e5:
        return f"₹{amount/1e5:.2f}L"
    elif amount >= 1e3:
        return f"₹{amount/1e3:.2f}K"
    else:
        return f"₹{amount:.2f}"


def format_number(num: float) -> str:
    """Format numbers in Indian format"""
    if num >= 1e9:
        return f"{num/1e9:.2f}B"
    elif num >= 1e7:
        return f"{num/1e7:.2f}Cr"
    elif num >= 1e5:
        return f"{num/1e5:.2f}L"
    elif num >= 1e3:
        return f"{num/1e3:.2f}K"
    else:
        return f"{num:.0f}"


def create_choropleth_map(df: pd.DataFrame, color_column: str, title: str) -> go.Figure:
    """Create a choropleth map for India"""
    fig = px.choropleth(
        df,
        locations='State',
        color=color_column,
        hover_name='State',
        title=title,
        color_continuous_scale='Viridis'
    )
    
    fig.update_layout(
        geo=dict(
            showframe=False,
            showcoastlines=True,
        ),
        height=600
    )
    
    return fig


def apply_filters(df: pd.DataFrame, state: str = None, year: int = None, quarter: int = None) -> pd.DataFrame:
    """Apply filters to dataframe"""
    filtered_df = df.copy()
    
    if state and state != 'All States':
        filtered_df = filtered_df[filtered_df['State'] == state]
    
    if year and year != 'All Years':
        filtered_df = filtered_df[filtered_df['Year'] == year]
    
    if quarter and quarter != 'All Quarters':
        filtered_df = filtered_df[filtered_df['Quarter'] == quarter]
    
    return filtered_df
