"""
PhonePe Pulse Dashboard - Home Page
A comprehensive analytics dashboard for PhonePe transaction data
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import sys
import os

# Add project root to Python path for imports
sys.path.insert(0, os.path.dirname(__file__))

from utils.data_loader import (
    load_aggregated_transactions, 
    load_aggregated_users, 
    load_aggregated_insurance,
    get_summary_stats,
    format_currency,
    format_number,
    get_theme_aware_styles,
    render_theme_aware_feature_card
)

# Set page config
st.set_page_config(
    page_title="🏠 Home",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #6739B7;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem;
    }
    
    
    .sidebar .stSelectbox > label {
        color: #6739B7;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


def main():
    # Header
    st.markdown('<h1 class="main-header">📱 PhonePe Pulse Dashboard</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Load data and get summary stats
    stats = get_summary_stats()
    
    if not stats:
        st.error("Unable to load data. Please check if all CSV files are present in the data/ folder.")
        return
    
    # Welcome Section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ## 🚀 Welcome to PhonePe Pulse Analytics
        
        This comprehensive dashboard provides deep insights into PhonePe's digital payment ecosystem across India. 
        Explore transaction patterns, user behavior, insurance trends, and geographic distributions through 
        interactive visualizations and detailed analytics.
        
        ### 🎯 Key Features:
        """)
        
        features = [
            "📊 <b>Overview Analytics</b> - Transaction distributions and geographic insights",
            "💳 <b>Transaction Analysis</b> - Detailed transaction patterns and trends",  
            "👥 <b>User Analytics</b> - User registration and app usage patterns",
            "🛡️ <b>Insurance Analytics</b> - Insurance adoption and regional analysis",
            "📈 <b>Trend Comparison</b> - Time-series analysis and comparative studies"
        ]
        
        # Apply theme-aware styles once
        styles = get_theme_aware_styles()
        st.markdown(styles['feature_card_styles'], unsafe_allow_html=True)
        st.markdown(styles['theme_detection_script'], unsafe_allow_html=True)
        
        # Render each feature card with theme-aware styling
        for feature in features:
            st.markdown(f'<div class="feature-card-adaptive">{feature}</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 📋 Navigation")
        st.info("""
        Use the sidebar to navigate between different sections:
        
        🏠 **Home** - Overview and quick stats
        
        📊 **Overview** - Geographic and type distributions
        
        💳 **Transactions** - Transaction analysis
        
        👥 **Users** - User behavior analytics
        
        🛡️ **Insurance** - Insurance insights
        
        📈 **Trends** - Comparative analysis
        """)
    
    # Quick Stats Section
    st.markdown("## 📈 Quick Statistics")
    
    # Create metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Transactions",
            value=format_number(stats['total_transactions']),
            help="Total number of transactions across all states and time periods"
        )
    
    with col2:
        st.metric(
            label="Total Transaction Value",
            value=format_currency(stats['total_transaction_amount']),
            help="Total monetary value of all transactions"
        )
    
    with col3:
        st.metric(
            label="Registered Users",
            value=format_number(stats['total_users']),
            help="Total number of registered PhonePe users"
        )
    
    with col4:
        st.metric(
            label="App Opens",
            value=format_number(stats['total_app_opens']),
            help="Total number of app opens recorded"
        )
    
    # Second row of metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Insurance Policies",
            value=format_number(stats['total_insurance_count']),
            help="Total number of insurance policies"
        )
    
    with col2:
        st.metric(
            label="Insurance Value",
            value=format_currency(stats['total_insurance_amount']),
            help="Total value of insurance transactions"
        )
    
    with col3:
        st.metric(
            label="States Covered",
            value=stats['unique_states'],
            help="Number of states/UTs covered in the data"
        )
    
    with col4:
        st.metric(
            label="Time Period",
            value=stats['years_covered'],
            help="Years covered in the dataset"
        )
    
    st.markdown("---")
    
    # Data Overview Section
    st.markdown("## 📊 Data Overview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Transaction type distribution
        trans_df = load_aggregated_transactions()
        if not trans_df.empty:
            type_summary = trans_df.groupby('Transaction_Type').agg({
                'Transaction_Count': 'sum',
                'Transaction_Amount': 'sum'
            }).reset_index()
            
            fig_pie = px.pie(
                type_summary, 
                values='Transaction_Count', 
                names='Transaction_Type',
                title="Transaction Distribution by Type",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            fig_pie.update_layout(height=400)
            st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Top 10 states by transaction count
        if not trans_df.empty:
            state_summary = trans_df.groupby('State').agg({
                'Transaction_Count': 'sum',
                'Transaction_Amount': 'sum'
            }).reset_index().sort_values('Transaction_Count', ascending=False).head(10)
            
            fig_bar = px.bar(
                state_summary,
                x='Transaction_Count',
                y='State',
                orientation='h',
                title="Top 10 States by Transaction Count",
                color='Transaction_Count',
                color_continuous_scale='Viridis'
            )
            fig_bar.update_layout(height=400)
            st.plotly_chart(fig_bar, use_container_width=True)
    
    # Recent Trends
    st.markdown("## 📈 Recent Trends")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Monthly transaction trends (using Year-Quarter as proxy)
        if not trans_df.empty:
            # Create a time period column
            trans_df['Time_Period'] = trans_df['Year'].astype(str) + '-Q' + trans_df['Quarter'].astype(str)
            
            time_trends = trans_df.groupby('Time_Period').agg({
                'Transaction_Count': 'sum',
                'Transaction_Amount': 'sum'
            }).reset_index()
            
            # Get recent 8 quarters
            time_trends = time_trends.tail(8)
            
            fig_line = px.line(
                time_trends,
                x='Time_Period',
                y='Transaction_Count',
                title="Transaction Count Trends (Recent Quarters)",
                markers=True
            )
            fig_line.update_layout(height=400)
            st.plotly_chart(fig_line, use_container_width=True)
    
    with col2:
        # User growth trends
        users_df = load_aggregated_users()
        if not users_df.empty:
            users_df['Time_Period'] = users_df['Year'].astype(str) + '-Q' + users_df['Quarter'].astype(str)
            
            user_trends = users_df.groupby('Time_Period').agg({
                'Registered_Users': 'sum',
                'App_Opens': 'sum'
            }).reset_index()
            
            # Get recent 8 quarters
            user_trends = user_trends.tail(8)
            
            fig_line2 = px.line(
                user_trends,
                x='Time_Period',
                y='Registered_Users',
                title="User Registration Trends (Recent Quarters)",
                markers=True,
                color_discrete_sequence=['#FF6B6B']
            )
            fig_line2.update_layout(height=400)
            st.plotly_chart(fig_line2, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; margin-top: 2rem;'>
        <p>📱 PhonePe Pulse Dashboard | Built with Streamlit & Plotly | Data Analytics & Visualization</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
