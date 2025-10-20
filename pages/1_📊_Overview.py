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
    format_number,
    create_enhanced_choropleth,
    create_transaction_type_filter_choropleth,
    load_india_geojson,
    get_state_name_mapping
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


def get_transaction_types(df):
    """Get unique transaction types for filtering"""
    return ['All Types'] + sorted(df['Transaction_Type'].unique().tolist())


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
    
    # Transaction type filter
    transaction_types = get_transaction_types(trans_df)
    selected_type = st.sidebar.selectbox("Select Transaction Type", transaction_types, key="overview_type")
    
    # Apply filters
    filtered_trans = apply_filters(trans_df, year=year_filter, quarter=quarter_filter)
    
    # Apply transaction type filter
    if selected_type and selected_type != 'All Types':
        filtered_trans = filtered_trans[filtered_trans['Transaction_Type'] == selected_type]
    
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
    
    # Geographic heatmaps with enhanced interactivity
    st.subheader("🗺️ Interactive Geographic Heatmaps")
    
    # Add interpretation guide
    with st.expander("ℹ️ How to interpret these maps"):
        st.markdown("""
        **Interactive State-wise Heatmaps:**
        - **Darker colors** indicate higher values (more transactions/amounts)
        - **Hover** over states to see exact values and state names
        - **Zoom and pan** the map for detailed exploration
        - Use the **filters on the left** to focus on specific years, quarters, or transaction types
        
        **Color Scales:**
        - 📊 **Transaction Count**: Viridis scale (purple to yellow)
        - 💰 **Transaction Amount**: Plasma scale (purple to pink to yellow)
        - 📈 **Average Value**: RdYlBu scale (red to yellow to blue)
        
        **Navigation:** Click on tabs below to switch between different metrics.
        """)
    
    tab1, tab2, tab3 = st.tabs(["📊 Transaction Count", "💰 Transaction Amount", "📈 Average Transaction Value"])
    
    with tab1:
        st.markdown("**Transaction Count Distribution** - Shows total number of transactions per state")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            state_data = filtered_trans.groupby('State')['Transaction_Count'].sum().reset_index()
            state_data = state_data.sort_values('Transaction_Count', ascending=False)
            
            # Create enhanced choropleth
            title_suffix = f" ({selected_type})" if selected_type != 'All Types' else ""
            fig_heat1 = create_enhanced_choropleth(
                state_data, 
                'Transaction_Count', 
                f"State-wise Transaction Count Distribution{title_suffix}",
                color_scale='Viridis'
            )
            
            st.plotly_chart(fig_heat1, use_container_width=True)
        
        with col2:
            # Show top 10 performers table
            st.markdown("**🏆 Top 10 States**")
            top_states_count = state_data.head(10).copy()
            top_states_count['Formatted_Count'] = top_states_count['Transaction_Count'].apply(format_number)
            display_df = top_states_count[['State', 'Formatted_Count']].copy()
            display_df.columns = ['State', 'Count']
            st.dataframe(display_df, use_container_width=True, hide_index=True, height=400)
    
    with tab2:
        st.markdown("**Transaction Amount Distribution** - Shows total transaction value per state")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            state_amount = filtered_trans.groupby('State')['Transaction_Amount'].sum().reset_index()
            state_amount = state_amount.sort_values('Transaction_Amount', ascending=False)
            
            title_suffix = f" ({selected_type})" if selected_type != 'All Types' else ""
            fig_heat2 = create_enhanced_choropleth(
                state_amount, 
                'Transaction_Amount', 
                f"State-wise Transaction Amount Distribution{title_suffix}",
                color_scale='Plasma'
            )
            
            st.plotly_chart(fig_heat2, use_container_width=True)
        
        with col2:
            # Show top 10 performers table
            st.markdown("**🏆 Top 10 States**")
            top_states_amount = state_amount.head(10).copy()
            top_states_amount['Formatted_Amount'] = top_states_amount['Transaction_Amount'].apply(format_currency)
            display_df = top_states_amount[['State', 'Formatted_Amount']].copy()
            display_df.columns = ['State', 'Amount']
            st.dataframe(display_df, use_container_width=True, hide_index=True, height=400)
    
    with tab3:
        st.markdown("**Average Transaction Value** - Shows average transaction amount per state")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Calculate average transaction value by state
            state_avg = filtered_trans.groupby('State').agg({
                'Transaction_Count': 'sum',
                'Transaction_Amount': 'sum'
            }).reset_index()
            
            state_avg['Avg_Transaction_Value'] = (
                state_avg['Transaction_Amount'] / state_avg['Transaction_Count']
            ).fillna(0)
            
            state_avg = state_avg.sort_values('Avg_Transaction_Value', ascending=False)
            
            title_suffix = f" ({selected_type})" if selected_type != 'All Types' else ""
            fig_heat3 = create_enhanced_choropleth(
                state_avg, 
                'Avg_Transaction_Value', 
                f"State-wise Average Transaction Value{title_suffix}",
                color_scale='RdYlBu'
            )
            
            st.plotly_chart(fig_heat3, use_container_width=True)
        
        with col2:
            # Show top 10 performers table
            st.markdown("**🏆 Top 10 States**")
            top_states_avg = state_avg.head(10).copy()
            top_states_avg['Formatted_Avg'] = top_states_avg['Avg_Transaction_Value'].apply(format_currency)
            display_df = top_states_avg[['State', 'Formatted_Avg']].copy()
            display_df.columns = ['State', 'Avg Value']
            st.dataframe(display_df, use_container_width=True, hide_index=True, height=400)
    
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
