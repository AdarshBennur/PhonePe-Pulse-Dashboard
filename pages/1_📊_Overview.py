"""
PhonePe Pulse Dashboard - Overview Page
Geographic insights, transaction distributions, and state-wise analytics
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sys
import os

# Add project root to Python path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.data_loader import (
    load_aggregated_transactions,
    load_map_transactions,
    load_top_performers,
    get_state_list,
    get_year_list,
    get_quarter_list,
    apply_filters,
    format_currency,
    format_number
)

# Set page config
st.set_page_config(
    page_title="Overview - PhonePe Pulse",
    page_icon="📊",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)


def create_india_choropleth(df, value_col, title):
    """Create choropleth map of India"""
    # State mapping for proper choropleth (you may need to adjust based on your data)
    state_mapping = {
        'Andhra Pradesh': 'AP', 'Arunachal Pradesh': 'AR', 'Assam': 'AS',
        'Bihar': 'BR', 'Chhattisgarh': 'CT', 'Goa': 'GA', 'Gujarat': 'GJ',
        'Haryana': 'HR', 'Himachal Pradesh': 'HP', 'Jharkhand': 'JH',
        'Karnataka': 'KA', 'Kerala': 'KL', 'Madhya Pradesh': 'MP',
        'Maharashtra': 'MH', 'Manipur': 'MN', 'Meghalaya': 'ML',
        'Mizoram': 'MZ', 'Nagaland': 'NL', 'Odisha': 'OR', 'Punjab': 'PB',
        'Rajasthan': 'RJ', 'Sikkim': 'SK', 'Tamil Nadu': 'TN',
        'Telangana': 'TG', 'Tripura': 'TR', 'Uttar Pradesh': 'UP',
        'Uttarakhand': 'UT', 'West Bengal': 'WB', 'Delhi': 'DL',
        'Jammu & Kashmir': 'JK', 'Ladakh': 'LA', 'Puducherry': 'PY',
        'Chandigarh': 'CH', 'Dadra and Nagar Haveli and Daman and Diu': 'DN',
        'Lakshadweep': 'LD', 'Andaman & Nicobar Islands': 'AN'
    }
    
    # Create a simple bar chart instead of choropleth for now
    fig = px.bar(
        df.head(20),  # Top 20 states
        x=value_col,
        y='State',
        orientation='h',
        title=title,
        color=value_col,
        color_continuous_scale='Viridis'
    )
    
    fig.update_layout(
        height=600,
        yaxis={'categoryorder': 'total ascending'}
    )
    
    return fig


def main():
    st.title("📊 Geographic Overview & Analytics")
    st.markdown("Explore transaction patterns across India with interactive geographic insights")
    st.markdown("---")
    
    # Load data
    trans_df = load_aggregated_transactions()
    map_df = load_map_transactions()
    top_df = load_top_performers()
    
    if trans_df.empty:
        st.error("No transaction data available!")
        return
    
    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    
    # Year filter
    years = ['All Years'] + get_year_list()
    selected_year = st.sidebar.selectbox("Select Year", years, key="overview_year")
    year_filter = None if selected_year == 'All Years' else selected_year
    
    # Quarter filter
    quarters = ['All Quarters'] + get_quarter_list()
    selected_quarter = st.sidebar.selectbox("Select Quarter", quarters, key="overview_quarter")
    quarter_filter = None if selected_quarter == 'All Quarters' else selected_quarter
    
    # Apply filters
    filtered_trans = apply_filters(trans_df, year=year_filter, quarter=quarter_filter)
    
    if filtered_trans.empty:
        st.warning("No data available for the selected filters!")
        return
    
    # Summary metrics
    st.subheader("📈 Overview Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_transactions = filtered_trans['Transaction_Count'].sum()
    total_amount = filtered_trans['Transaction_Amount'].sum()
    unique_states = filtered_trans['State'].nunique()
    avg_transaction = total_amount / total_transactions if total_transactions > 0 else 0
    
    with col1:
        st.metric("Total Transactions", format_number(total_transactions))
    
    with col2:
        st.metric("Total Amount", format_currency(total_amount))
    
    with col3:
        st.metric("States/UTs", unique_states)
    
    with col4:
        st.metric("Avg Transaction", format_currency(avg_transaction))
    
    st.markdown("---")
    
    # Main visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        # Transaction Type Distribution
        type_summary = filtered_trans.groupby('Transaction_Type').agg({
            'Transaction_Count': 'sum',
            'Transaction_Amount': 'sum'
        }).reset_index()
        
        fig_donut = px.pie(
            type_summary,
            values='Transaction_Count',
            names='Transaction_Type',
            title="Transaction Distribution by Type",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        
        fig_donut.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
        )
        
        fig_donut.update_layout(height=500)
        st.plotly_chart(fig_donut, use_container_width=True)
    
    with col2:
        # Top 15 States by Transaction Count
        state_summary = filtered_trans.groupby('State').agg({
            'Transaction_Count': 'sum',
            'Transaction_Amount': 'sum'
        }).reset_index().sort_values('Transaction_Count', ascending=False).head(15)
        
        fig_bar = px.bar(
            state_summary,
            x='Transaction_Count',
            y='State',
            orientation='h',
            title="Top 15 States by Transaction Count",
            color='Transaction_Count',
            color_continuous_scale='Viridis'
        )
        
        fig_bar.update_layout(
            height=500,
            yaxis={'categoryorder': 'total ascending'}
        )
        
        fig_bar.update_traces(
            hovertemplate='<b>%{y}</b><br>Transactions: %{x}<extra></extra>'
        )
        
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # Geographic heatmaps
    st.subheader("🗺️ Geographic Distribution")
    
    tab1, tab2 = st.tabs(["📊 Transaction Count Heatmap", "💰 Transaction Amount Heatmap"])
    
    with tab1:
        state_data = filtered_trans.groupby('State')['Transaction_Count'].sum().reset_index()
        state_data = state_data.sort_values('Transaction_Count', ascending=False)
        
        fig_heat1 = create_india_choropleth(
            state_data, 
            'Transaction_Count', 
            f"State-wise Transaction Count Distribution"
        )
        
        st.plotly_chart(fig_heat1, use_container_width=True)
        
        # Show top 10 performers table
        st.subheader("🏆 Top 10 States by Transaction Count")
        top_states_count = state_data.head(10).copy()
        top_states_count['Transaction_Count'] = top_states_count['Transaction_Count'].apply(format_number)
        st.dataframe(top_states_count, use_container_width=True, hide_index=True)
    
    with tab2:
        state_amount = filtered_trans.groupby('State')['Transaction_Amount'].sum().reset_index()
        state_amount = state_amount.sort_values('Transaction_Amount', ascending=False)
        
        fig_heat2 = create_india_choropleth(
            state_amount, 
            'Transaction_Amount', 
            f"State-wise Transaction Amount Distribution"
        )
        
        st.plotly_chart(fig_heat2, use_container_width=True)
        
        # Show top 10 performers table
        st.subheader("🏆 Top 10 States by Transaction Amount")
        top_states_amount = state_amount.head(10).copy()
        top_states_amount['Transaction_Amount'] = top_states_amount['Transaction_Amount'].apply(format_currency)
        st.dataframe(top_states_amount, use_container_width=True, hide_index=True)
    
    # District-wise analysis (if map data available)
    if not map_df.empty:
        st.subheader("🏘️ District-wise Analysis")
        
        # Filter map data
        filtered_map = apply_filters(map_df, year=year_filter, quarter=quarter_filter)
        
        if not filtered_map.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                # Top districts by transaction count
                district_summary = filtered_map.groupby('District').agg({
                    'Transaction_Count': 'sum',
                    'Transaction_Amount': 'sum'
                }).reset_index().sort_values('Transaction_Count', ascending=False).head(15)
                
                fig_district = px.bar(
                    district_summary,
                    x='Transaction_Count',
                    y='District',
                    orientation='h',
                    title="Top 15 Districts by Transaction Count",
                    color='Transaction_Count',
                    color_continuous_scale='Blues'
                )
                
                fig_district.update_layout(
                    height=500,
                    yaxis={'categoryorder': 'total ascending'}
                )
                
                st.plotly_chart(fig_district, use_container_width=True)
            
            with col2:
                # District performance metrics
                district_metrics = filtered_map.groupby('District').agg({
                    'Transaction_Count': 'sum',
                    'Transaction_Amount': 'sum'
                }).reset_index()
                
                district_metrics['Avg_Transaction'] = (
                    district_metrics['Transaction_Amount'] / district_metrics['Transaction_Count']
                )
                
                top_avg = district_metrics.nlargest(15, 'Avg_Transaction')
                
                fig_avg = px.bar(
                    top_avg,
                    x='Avg_Transaction',
                    y='District',
                    orientation='h',
                    title="Top 15 Districts by Average Transaction Value",
                    color='Avg_Transaction',
                    color_continuous_scale='Oranges'
                )
                
                fig_avg.update_layout(
                    height=500,
                    yaxis={'categoryorder': 'total ascending'}
                )
                
                st.plotly_chart(fig_avg, use_container_width=True)
    
    # Performance comparison
    st.subheader("⚖️ State Performance Comparison")
    
    # Create comprehensive state metrics
    state_performance = filtered_trans.groupby('State').agg({
        'Transaction_Count': 'sum',
        'Transaction_Amount': 'sum'
    }).reset_index()
    
    state_performance['Avg_Transaction_Value'] = (
        state_performance['Transaction_Amount'] / state_performance['Transaction_Count']
    )
    
    # Scatter plot showing relationship between volume and value
    fig_scatter = px.scatter(
        state_performance,
        x='Transaction_Count',
        y='Transaction_Amount',
        size='Avg_Transaction_Value',
        hover_name='State',
        title="State Performance: Transaction Volume vs Total Value",
        labels={
            'Transaction_Count': 'Total Transaction Count',
            'Transaction_Amount': 'Total Transaction Amount (₹)',
            'Avg_Transaction_Value': 'Avg Transaction Value'
        },
        color='Avg_Transaction_Value',
        color_continuous_scale='RdYlBu'
    )
    
    fig_scatter.update_layout(height=600)
    st.plotly_chart(fig_scatter, use_container_width=True)
    
    # Performance summary table
    st.subheader("📋 State Performance Summary")
    
    # Format the performance table
    display_performance = state_performance.copy()
    display_performance = display_performance.sort_values('Transaction_Amount', ascending=False)
    display_performance['Transaction_Count_Formatted'] = display_performance['Transaction_Count'].apply(format_number)
    display_performance['Transaction_Amount_Formatted'] = display_performance['Transaction_Amount'].apply(format_currency)
    display_performance['Avg_Transaction_Value_Formatted'] = display_performance['Avg_Transaction_Value'].apply(format_currency)
    
    # Show formatted table
    summary_table = display_performance[['State', 'Transaction_Count_Formatted', 'Transaction_Amount_Formatted', 'Avg_Transaction_Value_Formatted']].copy()
    summary_table.columns = ['State', 'Total Transactions', 'Total Amount', 'Avg Transaction Value']
    
    st.dataframe(summary_table, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
