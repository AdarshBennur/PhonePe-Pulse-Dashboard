"""
PhonePe Pulse Dashboard - Insurance Page
Insurance analytics including regional adoption, temporal trends, and value analysis
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
    load_aggregated_insurance,
    load_aggregated_transactions,
    load_aggregated_users,
    get_state_list,
    get_year_list,
    get_quarter_list,
    apply_filters,
    format_currency,
    format_number
)

# Set page config
st.set_page_config(
    page_title="Insurance - PhonePe Pulse",
    page_icon="🛡️",
    layout="wide"
)


def create_insurance_trends_chart(df):
    """Create insurance trends over time"""
    df['Time_Period'] = df['Year'].astype(str) + '-Q' + df['Quarter'].astype(str)
    
    trends_data = df.groupby('Time_Period').agg({
        'Insurance_Count': 'sum',
        'Insurance_Amount': 'sum'
    }).reset_index()
    
    trends_data['Avg_Policy_Value'] = trends_data['Insurance_Amount'] / trends_data['Insurance_Count']
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Insurance Policies Over Time', 'Average Policy Value Trend'),
        vertical_spacing=0.1
    )
    
    # Add insurance count
    fig.add_trace(
        go.Scatter(
            x=trends_data['Time_Period'],
            y=trends_data['Insurance_Count'],
            mode='lines+markers',
            name='Insurance Count',
            line=dict(color='#2E8B57', width=3)
        ),
        row=1, col=1
    )
    
    # Add average policy value
    fig.add_trace(
        go.Scatter(
            x=trends_data['Time_Period'],
            y=trends_data['Avg_Policy_Value'],
            mode='lines+markers',
            name='Avg Policy Value',
            line=dict(color='#FF6347', width=3)
        ),
        row=2, col=1
    )
    
    fig.update_layout(
        height=600,
        title_text="Insurance Trends Analysis",
        showlegend=False
    )
    
    return fig


def create_insurance_penetration_chart(insurance_df, users_df):
    """Create insurance penetration analysis"""
    # Calculate insurance penetration by state
    insurance_by_state = insurance_df.groupby('State').agg({
        'Insurance_Count': 'sum',
        'Insurance_Amount': 'sum'
    }).reset_index()
    
    users_by_state = users_df.groupby('State')['Registered_Users'].sum().reset_index()
    
    penetration_data = insurance_by_state.merge(users_by_state, on='State', how='inner')
    penetration_data['Insurance_Penetration'] = (
        penetration_data['Insurance_Count'] / penetration_data['Registered_Users'] * 100
    )
    
    penetration_data = penetration_data.sort_values('Insurance_Penetration', ascending=False).head(15)
    
    fig = px.bar(
        penetration_data,
        x='Insurance_Penetration',
        y='State',
        orientation='h',
        title="Top 15 States by Insurance Penetration (%)",
        color='Insurance_Penetration',
        color_continuous_scale='RdYlGn'
    )
    
    fig.update_layout(
        height=500,
        yaxis={'categoryorder': 'total ascending'},
        xaxis_title="Insurance Penetration (%)"
    )
    
    return fig


def main():
    st.title("🛡️ Insurance Analytics")
    st.markdown("Comprehensive analysis of insurance adoption, regional patterns, and market trends")
    st.markdown("---")
    
    # Load data
    insurance_df = load_aggregated_insurance()
    users_df = load_aggregated_users()
    trans_df = load_aggregated_transactions()
    
    if insurance_df.empty:
        st.error("No insurance data available!")
        return
    
    # Sidebar filters
    st.sidebar.header("🔍 Insurance Analytics Filters")
    
    # State filter
    states = ['All States'] + get_state_list()
    selected_state = st.sidebar.selectbox("Select State", states, key="insurance_state")
    state_filter = None if selected_state == 'All States' else selected_state
    
    # Year filter
    years = ['All Years'] + get_year_list()
    selected_year = st.sidebar.selectbox("Select Year", years, key="insurance_year")
    year_filter = None if selected_year == 'All Years' else selected_year
    
    # Quarter filter
    quarters = ['All Quarters'] + get_quarter_list()
    selected_quarter = st.sidebar.selectbox("Select Quarter", quarters, key="insurance_quarter")
    quarter_filter = None if selected_quarter == 'All Quarters' else selected_quarter
    
    # Apply filters
    filtered_insurance = apply_filters(insurance_df, state=state_filter, year=year_filter, quarter=quarter_filter)
    
    if filtered_insurance.empty:
        st.warning("No data available for the selected filters!")
        return
    
    # Summary metrics
    st.subheader("📊 Insurance Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_policies = filtered_insurance['Insurance_Count'].sum()
    total_value = filtered_insurance['Insurance_Amount'].sum()
    avg_policy_value = total_value / total_policies if total_policies > 0 else 0
    unique_states = filtered_insurance['State'].nunique()
    
    with col1:
        st.metric("Total Policies", format_number(total_policies))
    
    with col2:
        st.metric("Total Insurance Value", format_currency(total_value))
    
    with col3:
        st.metric("Average Policy Value", format_currency(avg_policy_value))
    
    with col4:
        st.metric("States Covered", unique_states)
    
    st.markdown("---")
    
    # Insurance trends analysis
    if len(filtered_insurance['Year'].unique()) > 1 or len(filtered_insurance['Quarter'].unique()) > 1:
        st.subheader("📈 Insurance Trends")
        
        trends_fig = create_insurance_trends_chart(filtered_insurance)
        st.plotly_chart(trends_fig, use_container_width=True)
        
        # Growth calculations
        col1, col2 = st.columns(2)
        
        filtered_insurance['Time_Period'] = (
            filtered_insurance['Year'].astype(str) + '-Q' + filtered_insurance['Quarter'].astype(str)
        )
        
        time_summary = filtered_insurance.groupby('Time_Period').agg({
            'Insurance_Count': 'sum',
            'Insurance_Amount': 'sum'
        }).reset_index().sort_values('Time_Period')
        
        if len(time_summary) > 1:
            policy_growth = ((time_summary.iloc[-1]['Insurance_Count'] - time_summary.iloc[0]['Insurance_Count']) / 
                           time_summary.iloc[0]['Insurance_Count'] * 100)
            
            value_growth = ((time_summary.iloc[-1]['Insurance_Amount'] - time_summary.iloc[0]['Insurance_Amount']) / 
                          time_summary.iloc[0]['Insurance_Amount'] * 100)
            
            with col1:
                st.success(f"""
                **Policy Count Growth:**  
                {policy_growth:.1f}% from {time_summary.iloc[0]['Time_Period']} to {time_summary.iloc[-1]['Time_Period']}
                """)
            
            with col2:
                st.success(f"""
                **Insurance Value Growth:**  
                {value_growth:.1f}% from {time_summary.iloc[0]['Time_Period']} to {time_summary.iloc[-1]['Time_Period']}
                """)
    
    # Regional analysis
    st.subheader("🗺️ Regional Insurance Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Top states by insurance count
        state_insurance = filtered_insurance.groupby('State').agg({
            'Insurance_Count': 'sum',
            'Insurance_Amount': 'sum'
        }).reset_index()
        
        state_insurance = state_insurance.sort_values('Insurance_Count', ascending=False).head(15)
        
        fig_states = px.bar(
            state_insurance,
            x='Insurance_Count',
            y='State',
            orientation='h',
            title="Top 15 States by Insurance Policies",
            color='Insurance_Count',
            color_continuous_scale='Blues'
        )
        
        fig_states.update_layout(
            height=500,
            yaxis={'categoryorder': 'total ascending'}
        )
        
        st.plotly_chart(fig_states, use_container_width=True)
    
    with col2:
        # Average policy value by state
        state_insurance['Avg_Policy_Value'] = (
            state_insurance['Insurance_Amount'] / state_insurance['Insurance_Count']
        )
        
        top_value_states = state_insurance.nlargest(15, 'Avg_Policy_Value')
        
        fig_values = px.bar(
            top_value_states,
            x='Avg_Policy_Value',
            y='State',
            orientation='h',
            title="Top 15 States by Average Policy Value",
            color='Avg_Policy_Value',
            color_continuous_scale='Oranges'
        )
        
        fig_values.update_layout(
            height=500,
            yaxis={'categoryorder': 'total ascending'}
        )
        
        st.plotly_chart(fig_values, use_container_width=True)
    
    # Insurance penetration analysis
    if not users_df.empty and state_filter is None:
        st.subheader("📊 Insurance Penetration Analysis")
        
        penetration_fig = create_insurance_penetration_chart(filtered_insurance, users_df)
        st.plotly_chart(penetration_fig, use_container_width=True)
        
        # Market insights
        col1, col2 = st.columns(2)
        
        with col1:
            # Insurance vs Transaction correlation
            if not trans_df.empty:
                # Calculate correlation between insurance and transactions
                insurance_state_summary = filtered_insurance.groupby('State')['Insurance_Count'].sum().reset_index()
                trans_state_summary = trans_df.groupby('State')['Transaction_Count'].sum().reset_index()
                
                correlation_data = insurance_state_summary.merge(trans_state_summary, on='State', how='inner')
                
                fig_correlation = px.scatter(
                    correlation_data,
                    x='Transaction_Count',
                    y='Insurance_Count',
                    hover_name='State',
                    title="Insurance vs Transaction Volume Correlation",
                    labels={
                        'Transaction_Count': 'Total Transactions',
                        'Insurance_Count': 'Total Insurance Policies'
                    },
                    trendline="ols"
                )
                
                fig_correlation.update_layout(height=400)
                st.plotly_chart(fig_correlation, use_container_width=True)
        
        with col2:
            # Market share analysis
            market_share = filtered_insurance.groupby('State')['Insurance_Amount'].sum().reset_index()
            market_share['Market_Share'] = (
                market_share['Insurance_Amount'] / market_share['Insurance_Amount'].sum() * 100
            )
            
            top_market_share = market_share.nlargest(10, 'Market_Share')
            
            fig_market = px.pie(
                top_market_share,
                values='Market_Share',
                names='State',
                title="Top 10 States by Insurance Market Share",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            
            fig_market.update_traces(textposition='inside', textinfo='percent+label')
            fig_market.update_layout(height=400)
            st.plotly_chart(fig_market, use_container_width=True)
    
    # Seasonal patterns
    st.subheader("📅 Seasonal Insurance Patterns")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Quarterly distribution
        quarterly_insurance = filtered_insurance.groupby('Quarter').agg({
            'Insurance_Count': 'sum',
            'Insurance_Amount': 'sum'
        }).reset_index()
        
        fig_quarterly = px.bar(
            quarterly_insurance,
            x='Quarter',
            y='Insurance_Count',
            title="Insurance Policies by Quarter",
            color='Insurance_Count',
            color_continuous_scale='Greens'
        )
        
        fig_quarterly.update_layout(height=400)
        st.plotly_chart(fig_quarterly, use_container_width=True)
    
    with col2:
        # Average policy value by quarter
        quarterly_insurance['Avg_Policy_Value'] = (
            quarterly_insurance['Insurance_Amount'] / quarterly_insurance['Insurance_Count']
        )
        
        fig_quarterly_value = px.line(
            quarterly_insurance,
            x='Quarter',
            y='Avg_Policy_Value',
            title="Average Policy Value by Quarter",
            markers=True
        )
        
        fig_quarterly_value.update_layout(height=400)
        st.plotly_chart(fig_quarterly_value, use_container_width=True)
    
    # Insurance performance matrix
    st.subheader("📋 Insurance Performance Matrix")
    
    # Create performance matrix
    performance_data = filtered_insurance.groupby('State').agg({
        'Insurance_Count': 'sum',
        'Insurance_Amount': 'sum'
    }).reset_index()
    
    performance_data['Avg_Policy_Value'] = (
        performance_data['Insurance_Amount'] / performance_data['Insurance_Count']
    )
    
    # Categorize performance
    performance_data['Volume_Category'] = pd.cut(
        performance_data['Insurance_Count'], 
        bins=3, 
        labels=['Low Volume', 'Medium Volume', 'High Volume']
    )
    
    performance_data['Value_Category'] = pd.cut(
        performance_data['Avg_Policy_Value'], 
        bins=3, 
        labels=['Low Value', 'Medium Value', 'High Value']
    )
    
    # Create performance scatter
    fig_performance = px.scatter(
        performance_data,
        x='Insurance_Count',
        y='Avg_Policy_Value',
        hover_name='State',
        size='Insurance_Amount',
        color='Volume_Category',
        title="Insurance Performance Matrix: Volume vs Average Policy Value",
        labels={
            'Insurance_Count': 'Total Insurance Policies',
            'Avg_Policy_Value': 'Average Policy Value (₹)'
        }
    )
    
    fig_performance.update_layout(height=500)
    st.plotly_chart(fig_performance, use_container_width=True)
    
    # Detailed insurance table
    st.subheader("📋 Detailed Insurance Analytics")
    
    # Format for display
    display_performance = performance_data.copy()
    display_performance = display_performance.sort_values('Insurance_Amount', ascending=False)
    display_performance['Insurance_Count'] = display_performance['Insurance_Count'].apply(format_number)
    display_performance['Insurance_Amount'] = display_performance['Insurance_Amount'].apply(format_currency)
    display_performance['Avg_Policy_Value'] = display_performance['Avg_Policy_Value'].apply(format_currency)
    
    # Select relevant columns for display
    display_columns = ['State', 'Insurance_Count', 'Insurance_Amount', 'Avg_Policy_Value']
    display_table = display_performance[display_columns].copy()
    display_table.columns = ['State', 'Total Policies', 'Total Value', 'Avg Policy Value']
    
    st.dataframe(display_table, use_container_width=True, hide_index=True)
    
    # Key insights
    st.subheader("💡 Key Insurance Insights")
    
    # Calculate insights
    top_policy_state = filtered_insurance.groupby('State')['Insurance_Count'].sum().idxmax()
    top_value_state = filtered_insurance.groupby('State')['Insurance_Amount'].sum().idxmax()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"""
        **Highest Policy Volume:**  
        {top_policy_state} with {format_number(filtered_insurance.groupby('State')['Insurance_Count'].sum().max())} policies
        """)
    
    with col2:
        st.info(f"""
        **Highest Insurance Value:**  
        {top_value_state} with {format_currency(filtered_insurance.groupby('State')['Insurance_Amount'].sum().max())}
        """)
    
    # Market concentration
    if len(performance_data) > 5:
        # Calculate market concentration (top 5 states' share)
        top_5_share = performance_data.nlargest(5, 'Insurance_Amount')['Insurance_Amount'].sum()
        total_market = performance_data['Insurance_Amount'].sum()
        concentration_ratio = (top_5_share / total_market * 100)
        
        high_value_states = len(performance_data[performance_data['Value_Category'] == 'High Value'])
        high_volume_states = len(performance_data[performance_data['Volume_Category'] == 'High Volume'])
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.success(f"""
            **Market Concentration:**  
            Top 5 states control {concentration_ratio:.1f}% of insurance value
            """)
        
        with col2:
            st.success(f"""
            **Premium Markets:**  
            {high_value_states} high-value states, {high_volume_states} high-volume states
            """)


if __name__ == "__main__":
    main()
