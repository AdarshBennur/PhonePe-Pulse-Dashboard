"""
PhonePe Pulse Dashboard - Trends & Comparison Page
Comparative analysis, time-series trends, and cross-metric insights
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import sys
import os

# Add project root to Python path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.data_loader import (
    load_aggregated_transactions,
    load_aggregated_users,
    load_aggregated_insurance,
    get_state_list,
    get_year_list,
    get_quarter_list,
    apply_filters,
    format_currency,
    format_number
)

# Set page config
st.set_page_config(
    page_title="Trends - PhonePe Pulse",
    page_icon="📈",
    layout="wide"
)


def create_comprehensive_trends_chart(trans_df, users_df, insurance_df):
    """Create comprehensive trends chart with multiple metrics"""
    # Prepare time series data
    trans_df['Time_Period'] = trans_df['Year'].astype(str) + '-Q' + trans_df['Quarter'].astype(str)
    users_df['Time_Period'] = users_df['Year'].astype(str) + '-Q' + users_df['Quarter'].astype(str)
    insurance_df['Time_Period'] = insurance_df['Year'].astype(str) + '-Q' + insurance_df['Quarter'].astype(str)
    
    # Aggregate by time period
    trans_trends = trans_df.groupby('Time_Period').agg({
        'Transaction_Count': 'sum',
        'Transaction_Amount': 'sum'
    }).reset_index()
    
    users_trends = users_df.groupby('Time_Period').agg({
        'Registered_Users': 'sum',
        'App_Opens': 'sum'
    }).reset_index()
    
    insurance_trends = insurance_df.groupby('Time_Period').agg({
        'Insurance_Count': 'sum',
        'Insurance_Amount': 'sum'
    }).reset_index()
    
    # Merge all trends
    all_trends = trans_trends.merge(users_trends, on='Time_Period', how='outer')
    all_trends = all_trends.merge(insurance_trends, on='Time_Period', how='outer')
    all_trends = all_trends.fillna(0).sort_values('Time_Period')
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Transaction Volume Trends',
            'User Growth Trends',
            'Insurance Adoption Trends',
            'Engagement Metrics'
        ),
        specs=[[{"secondary_y": True}, {"secondary_y": True}],
               [{"secondary_y": True}, {"secondary_y": True}]],
        vertical_spacing=0.1,
        horizontal_spacing=0.1
    )
    
    # Transaction trends
    fig.add_trace(
        go.Scatter(
            x=all_trends['Time_Period'],
            y=all_trends['Transaction_Count'],
            name='Transaction Count',
            line=dict(color='#1f77b4', width=2)
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=all_trends['Time_Period'],
            y=all_trends['Transaction_Amount'],
            name='Transaction Amount',
            line=dict(color='#ff7f0e', width=2),
            yaxis='y2'
        ),
        row=1, col=1, secondary_y=True
    )
    
    # User trends
    fig.add_trace(
        go.Scatter(
            x=all_trends['Time_Period'],
            y=all_trends['Registered_Users'],
            name='Registered Users',
            line=dict(color='#2ca02c', width=2)
        ),
        row=1, col=2
    )
    
    # Insurance trends
    fig.add_trace(
        go.Scatter(
            x=all_trends['Time_Period'],
            y=all_trends['Insurance_Count'],
            name='Insurance Policies',
            line=dict(color='#d62728', width=2)
        ),
        row=2, col=1
    )
    
    # Engagement metrics
    all_trends['Opens_per_User'] = all_trends['App_Opens'] / all_trends['Registered_Users']
    all_trends['Avg_Transaction'] = all_trends['Transaction_Amount'] / all_trends['Transaction_Count']
    
    fig.add_trace(
        go.Scatter(
            x=all_trends['Time_Period'],
            y=all_trends['Opens_per_User'],
            name='Opens per User',
            line=dict(color='#9467bd', width=2)
        ),
        row=2, col=2
    )
    
    fig.update_layout(
        height=700,
        title_text="Comprehensive PhonePe Pulse Trends Analysis",
        showlegend=True
    )
    
    return fig


def create_state_comparison_chart(df, states, metric, title):
    """Create comparison chart for selected states"""
    df['Time_Period'] = df['Year'].astype(str) + '-Q' + df['Quarter'].astype(str)
    
    comparison_data = df[df['State'].isin(states)].groupby(['Time_Period', 'State'])[metric].sum().reset_index()
    
    fig = px.line(
        comparison_data,
        x='Time_Period',
        y=metric,
        color='State',
        title=title,
        markers=True
    )
    
    fig.update_layout(
        height=400,
        xaxis_title="Time Period",
        yaxis_title=metric.replace('_', ' ').title()
    )
    
    return fig


def calculate_growth_rates(df, metric, period_col='Time_Period'):
    """Calculate period-over-period growth rates"""
    df = df.sort_values(period_col)
    df[f'{metric}_Growth_Rate'] = df[metric].pct_change() * 100
    return df


def main():
    st.title("📈 Trends & Comparative Analysis")
    st.markdown("Explore time-series trends, compare regions, and analyze cross-metric relationships")
    st.markdown("---")
    
    # Load all data
    trans_df = load_aggregated_transactions()
    users_df = load_aggregated_users()
    insurance_df = load_aggregated_insurance()
    
    if trans_df.empty or users_df.empty or insurance_df.empty:
        st.error("Required data not available for comprehensive analysis!")
        return
    
    # Sidebar for comparison settings
    st.sidebar.header("🔍 Comparison Settings")
    
    # Analysis type
    analysis_type = st.sidebar.selectbox(
        "Select Analysis Type",
        ["Comprehensive Trends", "State Comparison", "Metric Correlation", "Growth Analysis"],
        key="analysis_type"
    )
    
    if analysis_type == "Comprehensive Trends":
        st.subheader("📊 Comprehensive Trends Overview")
        
        # Time period filter
        years = get_year_list()
        if len(years) > 1:
            year_range = st.sidebar.slider(
                "Select Year Range",
                min_value=min(years),
                max_value=max(years),
                value=(min(years), max(years)),
                key="trend_year_range"
            )
            
            # Filter data by year range
            filtered_trans = trans_df[
                (trans_df['Year'] >= year_range[0]) & (trans_df['Year'] <= year_range[1])
            ]
            filtered_users = users_df[
                (users_df['Year'] >= year_range[0]) & (users_df['Year'] <= year_range[1])
            ]
            filtered_insurance = insurance_df[
                (insurance_df['Year'] >= year_range[0]) & (insurance_df['Year'] <= year_range[1])
            ]
        else:
            filtered_trans = trans_df
            filtered_users = users_df
            filtered_insurance = insurance_df
        
        # Create comprehensive trends chart
        trends_fig = create_comprehensive_trends_chart(filtered_trans, filtered_users, filtered_insurance)
        st.plotly_chart(trends_fig, use_container_width=True)
        
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        
        # Calculate overall growth
        trans_growth = ((filtered_trans.groupby('Year')['Transaction_Count'].sum().iloc[-1] - 
                        filtered_trans.groupby('Year')['Transaction_Count'].sum().iloc[0]) / 
                       filtered_trans.groupby('Year')['Transaction_Count'].sum().iloc[0] * 100)
        
        users_growth = ((filtered_users.groupby('Year')['Registered_Users'].sum().iloc[-1] - 
                        filtered_users.groupby('Year')['Registered_Users'].sum().iloc[0]) / 
                       filtered_users.groupby('Year')['Registered_Users'].sum().iloc[0] * 100)
        
        insurance_growth = ((filtered_insurance.groupby('Year')['Insurance_Count'].sum().iloc[-1] - 
                            filtered_insurance.groupby('Year')['Insurance_Count'].sum().iloc[0]) / 
                           filtered_insurance.groupby('Year')['Insurance_Count'].sum().iloc[0] * 100)
        
        with col1:
            st.metric("Transaction Growth", f"{trans_growth:.1f}%")
        
        with col2:
            st.metric("User Growth", f"{users_growth:.1f}%")
        
        with col3:
            st.metric("Insurance Growth", f"{insurance_growth:.1f}%")
    
    elif analysis_type == "State Comparison":
        st.subheader("⚖️ State-wise Comparison")
        
        # State selection
        available_states = get_state_list()
        selected_states = st.sidebar.multiselect(
            "Select States to Compare (max 5)",
            available_states,
            default=available_states[:3],
            max_selections=5,
            key="compare_states"
        )
        
        if not selected_states:
            st.warning("Please select at least one state for comparison.")
            return
        
        # Metric selection
        metric_options = {
            'Transaction_Count': 'Transaction Count',
            'Transaction_Amount': 'Transaction Amount',
            'Registered_Users': 'Registered Users',
            'App_Opens': 'App Opens',
            'Insurance_Count': 'Insurance Policies'
        }
        
        selected_metric = st.sidebar.selectbox(
            "Select Metric to Compare",
            list(metric_options.keys()),
            format_func=lambda x: metric_options[x],
            key="compare_metric"
        )
        
        # Create comparison charts
        col1, col2 = st.columns(2)
        
        with col1:
            if selected_metric in ['Transaction_Count', 'Transaction_Amount']:
                comp_fig1 = create_state_comparison_chart(
                    trans_df, selected_states, selected_metric,
                    f"{metric_options[selected_metric]} Comparison"
                )
                st.plotly_chart(comp_fig1, use_container_width=True)
            elif selected_metric in ['Registered_Users', 'App_Opens']:
                comp_fig1 = create_state_comparison_chart(
                    users_df, selected_states, selected_metric,
                    f"{metric_options[selected_metric]} Comparison"
                )
                st.plotly_chart(comp_fig1, use_container_width=True)
            elif selected_metric == 'Insurance_Count':
                comp_fig1 = create_state_comparison_chart(
                    insurance_df, selected_states, selected_metric,
                    f"{metric_options[selected_metric]} Comparison"
                )
                st.plotly_chart(comp_fig1, use_container_width=True)
        
        with col2:
            # Market share comparison
            if selected_metric in ['Transaction_Count', 'Transaction_Amount']:
                market_data = trans_df[trans_df['State'].isin(selected_states)]
            elif selected_metric in ['Registered_Users', 'App_Opens']:
                market_data = users_df[users_df['State'].isin(selected_states)]
            else:
                market_data = insurance_df[insurance_df['State'].isin(selected_states)]
            
            market_share = market_data.groupby('State')[selected_metric].sum().reset_index()
            market_share['Share'] = market_share[selected_metric] / market_share[selected_metric].sum() * 100
            
            fig_share = px.pie(
                market_share,
                values='Share',
                names='State',
                title=f"{metric_options[selected_metric]} Market Share"
            )
            
            fig_share.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_share, use_container_width=True)
        
        # Detailed comparison table
        st.subheader("📊 Detailed State Comparison")
        
        comparison_summary = []
        for state in selected_states:
            if selected_metric in ['Transaction_Count', 'Transaction_Amount']:
                state_data = trans_df[trans_df['State'] == state][selected_metric].sum()
            elif selected_metric in ['Registered_Users', 'App_Opens']:
                state_data = users_df[users_df['State'] == state][selected_metric].sum()
            else:
                state_data = insurance_df[insurance_df['State'] == state][selected_metric].sum()
            
            comparison_summary.append({
                'State': state,
                'Total': state_data,
                'Formatted': format_number(state_data) if 'Count' in selected_metric or 'Users' in selected_metric else format_currency(state_data)
            })
        
        comparison_df = pd.DataFrame(comparison_summary)
        comparison_df = comparison_df.sort_values('Total', ascending=False)
        
        display_df = comparison_df[['State', 'Formatted']].copy()
        display_df.columns = ['State', metric_options[selected_metric]]
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    elif analysis_type == "Metric Correlation":
        st.subheader("🔗 Cross-Metric Correlation Analysis")
        
        # Prepare correlation data
        correlation_data = trans_df.groupby('State').agg({
            'Transaction_Count': 'sum',
            'Transaction_Amount': 'sum'
        }).reset_index()
        
        user_data = users_df.groupby('State').agg({
            'Registered_Users': 'sum',
            'App_Opens': 'sum'
        }).reset_index()
        
        insurance_data = insurance_df.groupby('State').agg({
            'Insurance_Count': 'sum',
            'Insurance_Amount': 'sum'
        }).reset_index()
        
        # Merge all data
        merged_data = correlation_data.merge(user_data, on='State', how='inner')
        merged_data = merged_data.merge(insurance_data, on='State', how='inner')
        
        # Calculate derived metrics
        merged_data['Avg_Transaction_Value'] = merged_data['Transaction_Amount'] / merged_data['Transaction_Count']
        merged_data['Opens_per_User'] = merged_data['App_Opens'] / merged_data['Registered_Users']
        merged_data['Insurance_Penetration'] = merged_data['Insurance_Count'] / merged_data['Registered_Users']
        
        # Correlation selection
        correlation_metrics = [
            'Transaction_Count', 'Transaction_Amount', 'Registered_Users', 
            'App_Opens', 'Insurance_Count', 'Insurance_Amount',
            'Avg_Transaction_Value', 'Opens_per_User', 'Insurance_Penetration'
        ]
        
        col1, col2 = st.columns(2)
        
        with col1:
            x_metric = st.selectbox("Select X-axis Metric", correlation_metrics, key="corr_x")
        
        with col2:
            y_metric = st.selectbox("Select Y-axis Metric", correlation_metrics, index=1, key="corr_y")
        
        # Create correlation scatter plot
        fig_corr = px.scatter(
            merged_data,
            x=x_metric,
            y=y_metric,
            hover_name='State',
            title=f"Correlation: {x_metric} vs {y_metric}",
            trendline="ols"
        )
        
        fig_corr.update_layout(height=500)
        st.plotly_chart(fig_corr, use_container_width=True)
        
        # Correlation matrix
        st.subheader("📈 Correlation Matrix")
        
        numeric_columns = merged_data.select_dtypes(include=[np.number]).columns
        corr_matrix = merged_data[numeric_columns].corr()
        
        fig_heatmap = px.imshow(
            corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.index,
            title="Metrics Correlation Heatmap",
            color_continuous_scale='RdBu',
            aspect='auto'
        )
        
        fig_heatmap.update_layout(height=600)
        st.plotly_chart(fig_heatmap, use_container_width=True)
    
    elif analysis_type == "Growth Analysis":
        st.subheader("📊 Growth Rate Analysis")
        
        # Growth period selection
        growth_period = st.sidebar.selectbox(
            "Growth Analysis Period",
            ["Quarterly", "Yearly"],
            key="growth_period"
        )
        
        # Prepare growth data
        if growth_period == "Quarterly":
            trans_df['Time_Period'] = trans_df['Year'].astype(str) + '-Q' + trans_df['Quarter'].astype(str)
            users_df['Time_Period'] = users_df['Year'].astype(str) + '-Q' + users_df['Quarter'].astype(str)
            insurance_df['Time_Period'] = insurance_df['Year'].astype(str) + '-Q' + insurance_df['Quarter'].astype(str)
        else:
            trans_df['Time_Period'] = trans_df['Year'].astype(str)
            users_df['Time_Period'] = users_df['Year'].astype(str)
            insurance_df['Time_Period'] = insurance_df['Year'].astype(str)
        
        # Calculate growth rates
        trans_growth = trans_df.groupby('Time_Period')['Transaction_Count'].sum().reset_index()
        trans_growth = calculate_growth_rates(trans_growth, 'Transaction_Count')
        
        users_growth = users_df.groupby('Time_Period')['Registered_Users'].sum().reset_index()
        users_growth = calculate_growth_rates(users_growth, 'Registered_Users')
        
        insurance_growth = insurance_df.groupby('Time_Period')['Insurance_Count'].sum().reset_index()
        insurance_growth = calculate_growth_rates(insurance_growth, 'Insurance_Count')
        
        # Create growth rate comparison
        fig_growth = go.Figure()
        
        fig_growth.add_trace(go.Scatter(
            x=trans_growth['Time_Period'],
            y=trans_growth['Transaction_Count_Growth_Rate'],
            mode='lines+markers',
            name='Transaction Growth Rate',
            line=dict(color='#1f77b4', width=2)
        ))
        
        fig_growth.add_trace(go.Scatter(
            x=users_growth['Time_Period'],
            y=users_growth['Registered_Users_Growth_Rate'],
            mode='lines+markers',
            name='User Growth Rate',
            line=dict(color='#2ca02c', width=2)
        ))
        
        fig_growth.add_trace(go.Scatter(
            x=insurance_growth['Time_Period'],
            y=insurance_growth['Insurance_Count_Growth_Rate'],
            mode='lines+markers',
            name='Insurance Growth Rate',
            line=dict(color='#d62728', width=2)
        ))
        
        fig_growth.update_layout(
            title=f"{growth_period} Growth Rate Comparison",
            xaxis_title="Time Period",
            yaxis_title="Growth Rate (%)",
            height=500
        )
        
        st.plotly_chart(fig_growth, use_container_width=True)
        
        # Growth statistics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            avg_trans_growth = trans_growth['Transaction_Count_Growth_Rate'].mean()
            st.metric("Avg Transaction Growth", f"{avg_trans_growth:.1f}%")
        
        with col2:
            avg_user_growth = users_growth['Registered_Users_Growth_Rate'].mean()
            st.metric("Avg User Growth", f"{avg_user_growth:.1f}%")
        
        with col3:
            avg_insurance_growth = insurance_growth['Insurance_Count_Growth_Rate'].mean()
            st.metric("Avg Insurance Growth", f"{avg_insurance_growth:.1f}%")
    
    # Additional insights
    st.markdown("---")
    st.subheader("💡 Key Trend Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Top growing states
        state_growth = trans_df.groupby(['State', 'Year'])['Transaction_Count'].sum().reset_index()
        
        if len(state_growth['Year'].unique()) > 1:
            growth_analysis = []
            for state in state_growth['State'].unique():
                state_data = state_growth[state_growth['State'] == state].sort_values('Year')
                if len(state_data) > 1:
                    growth_rate = ((state_data.iloc[-1]['Transaction_Count'] - state_data.iloc[0]['Transaction_Count']) / 
                                 state_data.iloc[0]['Transaction_Count'] * 100)
                    growth_analysis.append({'State': state, 'Growth_Rate': growth_rate})
            
            if growth_analysis:
                growth_df = pd.DataFrame(growth_analysis)
                top_growing = growth_df.nlargest(5, 'Growth_Rate')
                
                st.success(f"""
                **Top Growing States (Transactions):**
                
                {chr(10).join([f"• {row['State']}: {row['Growth_Rate']:.1f}%" for _, row in top_growing.iterrows()])}
                """)
    
    with col2:
        # Market leaders
        current_leaders = trans_df.groupby('State')['Transaction_Count'].sum().nlargest(3)
        
        st.info(f"""
        **Current Market Leaders:**
        
        {chr(10).join([f"• {state}: {format_number(count)}" for state, count in current_leaders.items()])}
        """)


if __name__ == "__main__":
    main()
