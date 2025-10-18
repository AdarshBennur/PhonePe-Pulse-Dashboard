"""
PhonePe Pulse Dashboard - Users Page
User analytics including registration trends, app usage, and regional adoption
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
    load_aggregated_users,
    load_aggregated_transactions,
    get_state_list,
    get_year_list,
    get_quarter_list,
    apply_filters,
    format_number
)

# Set page config
st.set_page_config(
    page_title="Users - PhonePe Pulse",
    page_icon="👥",
    layout="wide"
)


def create_user_engagement_chart(df):
    """Create user engagement analysis chart"""
    df['Time_Period'] = df['Year'].astype(str) + '-Q' + df['Quarter'].astype(str)
    
    # Calculate engagement metrics
    engagement_data = df.groupby('Time_Period').agg({
        'Registered_Users': 'sum',
        'App_Opens': 'sum'
    }).reset_index()
    
    engagement_data['Opens_per_User'] = engagement_data['App_Opens'] / engagement_data['Registered_Users']
    
    # Create subplot
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('User Registration Over Time', 'App Opens per User'),
        vertical_spacing=0.1
    )
    
    # Add user registration line
    fig.add_trace(
        go.Scatter(
            x=engagement_data['Time_Period'],
            y=engagement_data['Registered_Users'],
            mode='lines+markers',
            name='Registered Users',
            line=dict(color='#1f77b4', width=3)
        ),
        row=1, col=1
    )
    
    # Add opens per user line
    fig.add_trace(
        go.Scatter(
            x=engagement_data['Time_Period'],
            y=engagement_data['Opens_per_User'],
            mode='lines+markers',
            name='Opens per User',
            line=dict(color='#ff7f0e', width=3)
        ),
        row=2, col=1
    )
    
    fig.update_layout(
        height=600,
        title_text="User Engagement Analysis",
        showlegend=False
    )
    
    return fig


def create_user_adoption_map(df):
    """Create user adoption heatmap"""
    state_users = df.groupby('State').agg({
        'Registered_Users': 'sum',
        'App_Opens': 'sum'
    }).reset_index()
    
    state_users['Opens_per_User'] = state_users['App_Opens'] / state_users['Registered_Users']
    state_users = state_users.sort_values('Registered_Users', ascending=False).head(20)
    
    fig = px.bar(
        state_users,
        x='Registered_Users',
        y='State',
        orientation='h',
        title="Top 20 States by User Registration",
        color='Opens_per_User',
        color_continuous_scale='RdYlBu',
        labels={'Opens_per_User': 'Avg Opens per User'}
    )
    
    fig.update_layout(
        height=600,
        yaxis={'categoryorder': 'total ascending'}
    )
    
    return fig


def main():
    st.title("👥 User Analytics")
    st.markdown("Analyze user registration patterns, app engagement, and regional adoption trends")
    st.markdown("---")
    
    # Load data
    users_df = load_aggregated_users()
    trans_df = load_aggregated_transactions()
    
    if users_df.empty:
        st.error("No user data available!")
        return
    
    # Sidebar filters
    st.sidebar.header("🔍 User Analytics Filters")
    
    # State filter
    states = ['All States'] + get_state_list()
    selected_state = st.sidebar.selectbox("Select State", states, key="users_state")
    state_filter = None if selected_state == 'All States' else selected_state
    
    # Year filter
    years = ['All Years'] + get_year_list()
    selected_year = st.sidebar.selectbox("Select Year", years, key="users_year")
    year_filter = None if selected_year == 'All Years' else selected_year
    
    # Quarter filter
    quarters = ['All Quarters'] + get_quarter_list()
    selected_quarter = st.sidebar.selectbox("Select Quarter", quarters, key="users_quarter")
    quarter_filter = None if selected_quarter == 'All Quarters' else selected_quarter
    
    # Apply filters
    filtered_users = apply_filters(users_df, state=state_filter, year=year_filter, quarter=quarter_filter)
    
    if filtered_users.empty:
        st.warning("No data available for the selected filters!")
        return
    
    # Summary metrics
    st.subheader("📊 User Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_users = filtered_users['Registered_Users'].sum()
    total_opens = filtered_users['App_Opens'].sum()
    avg_opens_per_user = total_opens / total_users if total_users > 0 else 0
    unique_states = filtered_users['State'].nunique()
    
    with col1:
        st.metric("Total Registered Users", format_number(total_users))
    
    with col2:
        st.metric("Total App Opens", format_number(total_opens))
    
    with col3:
        st.metric("Avg Opens per User", f"{avg_opens_per_user:.1f}")
    
    with col4:
        st.metric("States Covered", unique_states)
    
    st.markdown("---")
    
    # User engagement analysis
    if len(filtered_users['Year'].unique()) > 1 or len(filtered_users['Quarter'].unique()) > 1:
        st.subheader("📈 User Engagement Trends")
        
        engagement_fig = create_user_engagement_chart(filtered_users)
        st.plotly_chart(engagement_fig, use_container_width=True)
        
        # Growth metrics
        col1, col2 = st.columns(2)
        
        # Calculate growth if multiple time periods
        filtered_users['Time_Period'] = filtered_users['Year'].astype(str) + '-Q' + filtered_users['Quarter'].astype(str)
        time_summary = filtered_users.groupby('Time_Period').agg({
            'Registered_Users': 'sum',
            'App_Opens': 'sum'
        }).reset_index().sort_values('Time_Period')
        
        if len(time_summary) > 1:
            user_growth = ((time_summary.iloc[-1]['Registered_Users'] - time_summary.iloc[0]['Registered_Users']) / 
                          time_summary.iloc[0]['Registered_Users'] * 100)
            
            opens_growth = ((time_summary.iloc[-1]['App_Opens'] - time_summary.iloc[0]['App_Opens']) / 
                           time_summary.iloc[0]['App_Opens'] * 100)
            
            with col1:
                st.success(f"""
                **User Growth:**  
                {user_growth:.1f}% from {time_summary.iloc[0]['Time_Period']} to {time_summary.iloc[-1]['Time_Period']}
                """)
            
            with col2:
                st.success(f"""
                **App Opens Growth:**  
                {opens_growth:.1f}% from {time_summary.iloc[0]['Time_Period']} to {time_summary.iloc[-1]['Time_Period']}
                """)
    
    # Geographic distribution
    st.subheader("🗺️ Geographic User Distribution")
    
    if state_filter is None:
        # Show state-wise distribution
        adoption_fig = create_user_adoption_map(filtered_users)
        st.plotly_chart(adoption_fig, use_container_width=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # User density by state
            state_summary = filtered_users.groupby('State').agg({
                'Registered_Users': 'sum',
                'App_Opens': 'sum'
            }).reset_index()
            
            state_summary['Opens_per_User'] = state_summary['App_Opens'] / state_summary['Registered_Users']
            top_engagement = state_summary.nlargest(15, 'Opens_per_User')
            
            fig_engagement = px.bar(
                top_engagement,
                x='Opens_per_User',
                y='State',
                orientation='h',
                title="Top 15 States by User Engagement",
                color='Opens_per_User',
                color_continuous_scale='Greens'
            )
            
            fig_engagement.update_layout(
                height=500,
                yaxis={'categoryorder': 'total ascending'}
            )
            
            st.plotly_chart(fig_engagement, use_container_width=True)
        
        with col2:
            # User penetration analysis (if transaction data available)
            if not trans_df.empty:
                # Calculate user-to-transaction ratio
                trans_summary = trans_df.groupby('State')['Transaction_Count'].sum().reset_index()
                user_trans_ratio = state_summary.merge(trans_summary, on='State', how='inner')
                user_trans_ratio['Transactions_per_User'] = user_trans_ratio['Transaction_Count'] / user_trans_ratio['Registered_Users']
                
                top_activity = user_trans_ratio.nlargest(15, 'Transactions_per_User')
                
                fig_activity = px.bar(
                    top_activity,
                    x='Transactions_per_User',
                    y='State',
                    orientation='h',
                    title="Top 15 States by Transactions per User",
                    color='Transactions_per_User',
                    color_continuous_scale='Blues'
                )
                
                fig_activity.update_layout(
                    height=500,
                    yaxis={'categoryorder': 'total ascending'}
                )
                
                st.plotly_chart(fig_activity, use_container_width=True)
    
    # User behavior patterns
    st.subheader("🎯 User Behavior Patterns")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Quarterly user registration patterns
        quarterly_users = filtered_users.groupby('Quarter')['Registered_Users'].sum().reset_index()
        
        fig_quarterly = px.bar(
            quarterly_users,
            x='Quarter',
            y='Registered_Users',
            title="User Registration by Quarter",
            color='Registered_Users',
            color_continuous_scale='Purples'
        )
        
        fig_quarterly.update_layout(height=400)
        st.plotly_chart(fig_quarterly, use_container_width=True)
    
    with col2:
        # App usage intensity
        usage_data = filtered_users.copy()
        usage_data['Opens_per_User'] = usage_data['App_Opens'] / usage_data['Registered_Users']
        usage_summary = usage_data.groupby('Quarter')['Opens_per_User'].mean().reset_index()
        
        fig_usage = px.line(
            usage_summary,
            x='Quarter',
            y='Opens_per_User',
            title="Average App Opens per User by Quarter",
            markers=True
        )
        
        fig_usage.update_layout(height=400)
        st.plotly_chart(fig_usage, use_container_width=True)
    
    # User segments analysis
    st.subheader("📊 User Segments Analysis")
    
    # Categorize states by user behavior
    state_behavior = filtered_users.groupby('State').agg({
        'Registered_Users': 'sum',
        'App_Opens': 'sum'
    }).reset_index()
    
    state_behavior['Opens_per_User'] = state_behavior['App_Opens'] / state_behavior['Registered_Users']
    
    # Create segments based on user count and engagement
    state_behavior['User_Segment'] = pd.cut(
        state_behavior['Registered_Users'], 
        bins=3, 
        labels=['Low Adoption', 'Medium Adoption', 'High Adoption']
    )
    
    state_behavior['Engagement_Segment'] = pd.cut(
        state_behavior['Opens_per_User'], 
        bins=3, 
        labels=['Low Engagement', 'Medium Engagement', 'High Engagement']
    )
    
    # Create segment distribution
    segment_dist = state_behavior.groupby(['User_Segment', 'Engagement_Segment']).size().reset_index(name='Count')
    
    fig_segments = px.sunburst(
        segment_dist,
        path=['User_Segment', 'Engagement_Segment'],
        values='Count',
        title="User Segments Distribution"
    )
    
    fig_segments.update_layout(height=500)
    st.plotly_chart(fig_segments, use_container_width=True)
    
    # Detailed user table
    st.subheader("📋 Detailed User Analytics")
    
    # Prepare detailed table
    if state_filter:
        detail_data = filtered_users.groupby(['Year', 'Quarter']).agg({
            'Registered_Users': 'sum',
            'App_Opens': 'sum'
        }).reset_index()
        detail_data['Opens_per_User'] = detail_data['App_Opens'] / detail_data['Registered_Users']
    else:
        detail_data = filtered_users.groupby('State').agg({
            'Registered_Users': 'sum',
            'App_Opens': 'sum'
        }).reset_index()
        detail_data['Opens_per_User'] = detail_data['App_Opens'] / detail_data['Registered_Users']
        detail_data = detail_data.sort_values('Registered_Users', ascending=False)
    
    # Format for display
    display_data = detail_data.copy()
    display_data['Registered_Users'] = display_data['Registered_Users'].apply(format_number)
    display_data['App_Opens'] = display_data['App_Opens'].apply(format_number)
    display_data['Opens_per_User'] = display_data['Opens_per_User'].round(1)
    
    st.dataframe(display_data, use_container_width=True, hide_index=True)
    
    # Key insights
    st.subheader("💡 Key User Insights")
    
    # Calculate insights
    top_user_state = filtered_users.groupby('State')['Registered_Users'].sum().idxmax()
    top_engagement_state = state_behavior.loc[state_behavior['Opens_per_User'].idxmax(), 'State']
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"""
        **Highest User Base:**  
        {top_user_state} with {format_number(filtered_users.groupby('State')['Registered_Users'].sum().max())} users
        """)
    
    with col2:
        st.info(f"""
        **Highest Engagement:**  
        {top_engagement_state} with {state_behavior['Opens_per_User'].max():.1f} opens per user
        """)
    
    # User distribution by segments
    if len(state_behavior) > 5:
        high_adoption_states = len(state_behavior[state_behavior['User_Segment'] == 'High Adoption'])
        high_engagement_states = len(state_behavior[state_behavior['Engagement_Segment'] == 'High Engagement'])
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.success(f"""
            **High Adoption States:**  
            {high_adoption_states} states with high user adoption
            """)
        
        with col2:
            st.success(f"""
            **High Engagement States:**  
            {high_engagement_states} states with high user engagement
            """)


if __name__ == "__main__":
    main()
