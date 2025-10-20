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


def get_theme_aware_styles():
    """
    Get theme-aware CSS styles that adapt to light/dark mode.
    Returns appropriate colors for text and backgrounds based on the current theme.
    """
    return {
        'feature_card_styles': """
        <style>
            .feature-card-adaptive {
                padding: 1rem;
                border-radius: 8px;
                border-left: 4px solid #6739B7;
                margin: 0.5rem 0;
                transition: all 0.3s ease;
            }
            
            /* Use CSS custom properties that adapt to Streamlit themes */
            .feature-card-adaptive {
                background-color: rgba(var(--secondary-background-color-rgb, 248, 249, 250), 0.8);
                color: var(--text-color, #333333);
                border: 1px solid rgba(128, 128, 128, 0.2);
            }
            
            /* Fallback: Use CSS media queries for system preference */
            @media (prefers-color-scheme: dark) {
                .feature-card-adaptive {
                    background-color: rgba(255, 255, 255, 0.08) !important;
                    color: #ffffff !important;
                    border: 1px solid rgba(255, 255, 255, 0.15) !important;
                }
            }
            
            @media (prefers-color-scheme: light) {
                .feature-card-adaptive {
                    background-color: #f8f9fa !important;
                    color: #333333 !important;
                    border: 1px solid rgba(128, 128, 128, 0.2) !important;
                }
            }
            
            /* Enhanced styling for better visibility */
            .feature-card-adaptive b {
                color: inherit;
                font-weight: 600;
            }
            
            .feature-card-adaptive:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            }
            
            /* Dark mode hover effect */
            @media (prefers-color-scheme: dark) {
                .feature-card-adaptive:hover {
                    box-shadow: 0 4px 12px rgba(255, 255, 255, 0.1) !important;
                }
            }
        </style>
        """,
        
        'theme_detection_script': """
        <script>
            // Theme detection and adaptation script
            function adaptToTheme() {
                // Try to detect Streamlit's current theme
                const streamlitApp = document.querySelector('[data-testid="stApp"]');
                if (streamlitApp) {
                    const computedStyle = window.getComputedStyle(streamlitApp);
                    const backgroundColor = computedStyle.backgroundColor;
                    
                    // Parse RGB values to determine if it's dark or light theme
                    const rgb = backgroundColor.match(/\\d+/g);
                    if (rgb && rgb.length >= 3) {
                        const [r, g, b] = rgb.map(Number);
                        const brightness = (r * 299 + g * 587 + b * 114) / 1000;
                        
                        // Apply theme-specific styles
                        const cards = document.querySelectorAll('.feature-card-adaptive');
                        cards.forEach(card => {
                            if (brightness < 128) { // Dark theme
                                card.style.backgroundColor = 'rgba(255, 255, 255, 0.08)';
                                card.style.color = '#ffffff';
                                card.style.border = '1px solid rgba(255, 255, 255, 0.15)';
                            } else { // Light theme
                                card.style.backgroundColor = '#f8f9fa';
                                card.style.color = '#333333';
                                card.style.border = '1px solid rgba(128, 128, 128, 0.2)';
                            }
                        });
                    }
                }
            }
            
            // Run adaptation immediately and on changes
            adaptToTheme();
            
            // Watch for theme changes
            const observer = new MutationObserver(adaptToTheme);
            if (document.body) {
                observer.observe(document.body, { 
                    attributes: true, 
                    attributeFilter: ['class', 'style'],
                    childList: true, 
                    subtree: true 
                });
            }
            
            // Also listen for system theme changes
            if (window.matchMedia) {
                window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', adaptToTheme);
            }
        </script>
        """
    }


def render_theme_aware_feature_card(content):
    """
    Render a theme-aware feature card with proper contrast in both light and dark modes.
    
    Args:
        content (str): The HTML content to display inside the card
    
    Returns:
        str: Complete HTML with theme-aware styling
    """
    styles = get_theme_aware_styles()
    
    return f"""
    {styles['feature_card_styles']}
    {styles['theme_detection_script']}
    <div class="feature-card-adaptive">{content}</div>
    """
