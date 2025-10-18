"""
PhonePe Pulse Dashboard - Transactions Page
Detailed transaction analysis with filtering and trend visualization
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import sys
import os

# Add project root to Python path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.data_loader import (
    load_aggregated_transactions,
    get_state_list,
    get_year_list,
    get_quarter_list,
    apply_filters,
    format_currency,
    format_number
)

# Set page config
st.set_page_config(
    page_title="Transactions - PhonePe Pulse",
    page_icon="💳",
    layout="wide"
)


def create_time_series_chart(df, value_col, title):
    """Create time series chart"""
    df['Time_Period'] = df['Year'].astype(str) + '-Q' + df['Quarter'].astype(str)
    
    time_data = df.groupby(['Time_Period', 'Transaction_Type'])[value_col].sum().reset_index()
    
    fig = px.line(
        time_data,
        x='Time_Period',
        y=value_col,
        color='Transaction_Type',
        title=title,
        markers=True
    )
    
    fig.update_layout(
        height=500,
        xaxis_title="Time Period (Year-Quarter)",
        yaxis_title=value_col.replace('_', ' ').title()
    )
    
    return fig


def create_transaction_heatmap(df):
    """Create heatmap for transaction patterns"""
    heatmap_data = df.groupby(['State', 'Transaction_Type'])['Transaction_Count'].sum().reset_index()
    
    # Pivot for heatmap
    pivot_data = heatmap_data.pivot(index='State', columns='Transaction_Type', values='Transaction_Count').fillna(0)
    
    fig = px.imshow(
        pivot_data.values,
        x=pivot_data.columns,
        y=pivot_data.index,
        title="Transaction Type Distribution Across States",
        aspect='auto',
        color_continuous_scale='Viridis'
    )
    
    fig.update_layout(height=600)
    return fig


def main():
    st.title("💳 Transaction Analytics")
    st.markdown("Deep dive into transaction patterns, types, and temporal trends")
    st.markdown("---")
    
    # Load data
    trans_df = load_aggregated_transactions()
    
    if trans_df.empty:
        st.error("No transaction data available!")
        return
    
    # Sidebar filters
    st.sidebar.header("🔍 Transaction Filters")
    
    # State filter
    states = ['All States'] + get_state_list()
    selected_state = st.sidebar.selectbox("Select State", states, key="trans_state")
    state_filter = None if selected_state == 'All States' else selected_state
    
    # Year filter
    years = ['All Years'] + get_year_list()
    selected_year = st.sidebar.selectbox("Select Year", years, key="trans_year")
    year_filter = None if selected_year == 'All Years' else selected_year
    
    # Quarter filter
    quarters = ['All Quarters'] + get_quarter_list()
    selected_quarter = st.sidebar.selectbox("Select Quarter", quarters, key="trans_quarter")
    quarter_filter = None if selected_quarter == 'All Quarters' else selected_quarter
    
    # Transaction type filter
    transaction_types = ['All Types'] + list(trans_df['Transaction_Type'].unique())
    selected_type = st.sidebar.selectbox("Select Transaction Type", transaction_types, key="trans_type")
    
    # Apply filters
    filtered_df = apply_filters(trans_df, state=state_filter, year=year_filter, quarter=quarter_filter)
    
    if selected_type != 'All Types':
        filtered_df = filtered_df[filtered_df['Transaction_Type'] == selected_type]
    
    if filtered_df.empty:
        st.warning("No data available for the selected filters!")
        return
    
    # Summary metrics
    st.subheader("📊 Transaction Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_count = filtered_df['Transaction_Count'].sum()
    total_amount = filtered_df['Transaction_Amount'].sum()
    avg_transaction = total_amount / total_count if total_count > 0 else 0
    unique_types = filtered_df['Transaction_Type'].nunique()
    
    with col1:
        st.metric("Total Transactions", format_number(total_count))
    
    with col2:
        st.metric("Total Amount", format_currency(total_amount))
    
    with col3:
        st.metric("Average Transaction", format_currency(avg_transaction))
    
    with col4:
        st.metric("Transaction Types", unique_types)
    
    st.markdown("---")
    
    # Transaction type analysis
    st.subheader("🔄 Transaction Type Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Transaction count by type
        type_count = filtered_df.groupby('Transaction_Type')['Transaction_Count'].sum().reset_index()
        type_count = type_count.sort_values('Transaction_Count', ascending=True)
        
        fig_count = px.bar(
            type_count,
            x='Transaction_Count',
            y='Transaction_Type',
            orientation='h',
            title="Transaction Count by Type",
            color='Transaction_Count',
            color_continuous_scale='Blues'
        )
        
        fig_count.update_layout(height=400)
        st.plotly_chart(fig_count, use_container_width=True)
    
    with col2:
        # Transaction amount by type
        type_amount = filtered_df.groupby('Transaction_Type')['Transaction_Amount'].sum().reset_index()
        type_amount = type_amount.sort_values('Transaction_Amount', ascending=True)
        
        fig_amount = px.bar(
            type_amount,
            x='Transaction_Amount',
            y='Transaction_Type',
            orientation='h',
            title="Transaction Amount by Type",
            color='Transaction_Amount',
            color_continuous_scale='Oranges'
        )
        
        fig_amount.update_layout(height=400)
        st.plotly_chart(fig_amount, use_container_width=True)
    
    # Time series analysis
    st.subheader("📈 Time Series Analysis")
    
    if len(filtered_df['Year'].unique()) > 1 or len(filtered_df['Quarter'].unique()) > 1:
        tab1, tab2 = st.tabs(["📊 Transaction Count Trends", "💰 Transaction Amount Trends"])
        
        with tab1:
            fig_ts_count = create_time_series_chart(filtered_df, 'Transaction_Count', 'Transaction Count Over Time')
            st.plotly_chart(fig_ts_count, use_container_width=True)
        
        with tab2:
            fig_ts_amount = create_time_series_chart(filtered_df, 'Transaction_Amount', 'Transaction Amount Over Time')
            st.plotly_chart(fig_ts_amount, use_container_width=True)
    else:
        st.info("Time series analysis requires data from multiple time periods. Please adjust your filters.")
    
    # Geographic analysis (if multiple states)
    if state_filter is None and len(filtered_df['State'].unique()) > 1:
        st.subheader("🗺️ Geographic Distribution")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Top states by transaction count
            state_count = filtered_df.groupby('State')['Transaction_Count'].sum().reset_index()
            state_count = state_count.sort_values('Transaction_Count', ascending=False).head(15)
            
            fig_state_count = px.bar(
                state_count,
                x='State',
                y='Transaction_Count',
                title="Top 15 States by Transaction Count",
                color='Transaction_Count',
                color_continuous_scale='Viridis'
            )
            
            fig_state_count.update_layout(
                height=500,
                xaxis={'tickangle': 45}
            )
            
            st.plotly_chart(fig_state_count, use_container_width=True)
        
        with col2:
            # State performance scatter
            state_metrics = filtered_df.groupby('State').agg({
                'Transaction_Count': 'sum',
                'Transaction_Amount': 'sum'
            }).reset_index()
            
            state_metrics['Avg_Transaction'] = (
                state_metrics['Transaction_Amount'] / state_metrics['Transaction_Count']
            )
            
            fig_scatter = px.scatter(
                state_metrics,
                x='Transaction_Count',
                y='Avg_Transaction',
                hover_name='State',
                title="State Performance: Volume vs Average Value",
                labels={
                    'Transaction_Count': 'Total Transactions',
                    'Avg_Transaction': 'Average Transaction Value (₹)'
                },
                color='Transaction_Amount',
                size='Transaction_Count',
                color_continuous_scale='RdYlBu'
            )
            
            fig_scatter.update_layout(height=500)
            st.plotly_chart(fig_scatter, use_container_width=True)
    
    # Transaction pattern heatmap
    if len(filtered_df['State'].unique()) > 5 and len(filtered_df['Transaction_Type'].unique()) > 1:
        st.subheader("🔥 Transaction Pattern Heatmap")
        
        heatmap_fig = create_transaction_heatmap(filtered_df)
        st.plotly_chart(heatmap_fig, use_container_width=True)
    
    # Detailed breakdown
    st.subheader("📋 Detailed Transaction Breakdown")
    
    # Group by relevant dimensions
    if state_filter:
        # If state is filtered, show quarterly/yearly breakdown
        breakdown = filtered_df.groupby(['Year', 'Quarter', 'Transaction_Type']).agg({
            'Transaction_Count': 'sum',
            'Transaction_Amount': 'sum'
        }).reset_index()
        breakdown['Avg_Transaction'] = breakdown['Transaction_Amount'] / breakdown['Transaction_Count']
    else:
        # If no state filter, show state-wise breakdown
        breakdown = filtered_df.groupby(['State', 'Transaction_Type']).agg({
            'Transaction_Count': 'sum',
            'Transaction_Amount': 'sum'
        }).reset_index()
        breakdown['Avg_Transaction'] = breakdown['Transaction_Amount'] / breakdown['Transaction_Count']
    
    # Format for display
    display_breakdown = breakdown.copy()
    display_breakdown['Transaction_Count'] = display_breakdown['Transaction_Count'].apply(format_number)
    display_breakdown['Transaction_Amount'] = display_breakdown['Transaction_Amount'].apply(format_currency)
    display_breakdown['Avg_Transaction'] = display_breakdown['Avg_Transaction'].apply(format_currency)
    
    # Sort by total amount
    if 'State' in display_breakdown.columns:
        display_breakdown = display_breakdown.sort_values('Transaction_Amount', ascending=False)
    
    st.dataframe(display_breakdown, use_container_width=True, hide_index=True)
    
    # Performance insights
    st.subheader("💡 Key Insights")
    
    # Calculate insights
    top_type = filtered_df.groupby('Transaction_Type')['Transaction_Count'].sum().idxmax()
    top_type_count = filtered_df.groupby('Transaction_Type')['Transaction_Count'].sum().max()
    
    highest_avg_type = filtered_df.groupby('Transaction_Type').apply(
        lambda x: x['Transaction_Amount'].sum() / x['Transaction_Count'].sum()
    ).idxmax()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"""
        **Most Popular Transaction Type:**  
        {top_type} with {format_number(top_type_count)} transactions
        """)
    
    with col2:
        st.info(f"""
        **Highest Average Value Type:**  
        {highest_avg_type}
        """)
    
    # Growth analysis (if temporal data available)
    if len(filtered_df['Year'].unique()) > 1:
        # Calculate year-over-year growth
        yearly_data = filtered_df.groupby('Year').agg({
            'Transaction_Count': 'sum',
            'Transaction_Amount': 'sum'
        }).reset_index().sort_values('Year')
        
        if len(yearly_data) > 1:
            count_growth = ((yearly_data.iloc[-1]['Transaction_Count'] - yearly_data.iloc[0]['Transaction_Count']) / 
                           yearly_data.iloc[0]['Transaction_Count'] * 100)
            
            amount_growth = ((yearly_data.iloc[-1]['Transaction_Amount'] - yearly_data.iloc[0]['Transaction_Amount']) / 
                           yearly_data.iloc[0]['Transaction_Amount'] * 100)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.success(f"""
                **Transaction Count Growth:**  
                {count_growth:.1f}% from {yearly_data.iloc[0]['Year']} to {yearly_data.iloc[-1]['Year']}
                """)
            
            with col2:
                st.success(f"""
                **Transaction Amount Growth:**  
                {amount_growth:.1f}% from {yearly_data.iloc[0]['Year']} to {yearly_data.iloc[-1]['Year']}
                """)


if __name__ == "__main__":
    main()
