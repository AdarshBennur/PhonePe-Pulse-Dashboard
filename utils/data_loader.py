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


@st.cache_data
def load_india_geojson():
    """
    Load India states GeoJSON data with automated fetch capability.
    Returns GeoJSON data for choropleth maps.
    """
    import requests
    import json
    
    try:
        # Try to load from a reliable GeoJSON source
        # Using a trusted India states GeoJSON from GitHub
        geojson_url = "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
        
        response = requests.get(geojson_url, timeout=10)
        response.raise_for_status()
        
        geojson_data = response.json()
        
        # Verify the GeoJSON structure
        if 'features' not in geojson_data:
            raise ValueError("Invalid GeoJSON structure: missing 'features'")
            
        return geojson_data
        
    except Exception as e:
        st.error(f"Failed to load India GeoJSON data: {str(e)}")
        # Return empty GeoJSON structure as fallback
        return {"type": "FeatureCollection", "features": []}


@st.cache_data
def get_state_name_mapping():
    """
    Create comprehensive state name mapping between CSV data and GeoJSON.
    Maps CSV state names to exact GeoJSON ST_NM property values.
    """
    return {
        # CSV State Name -> GeoJSON ST_NM Property Value
        'Andhra Pradesh': 'Andhra Pradesh',
        'Arunachal Pradesh': 'Arunachal Pradesh', 
        'Assam': 'Assam',
        'Bihar': 'Bihar',
        'Chhattisgarh': 'Chhattisgarh',
        'Goa': 'Goa',
        'Gujarat': 'Gujarat',
        'Haryana': 'Haryana',
        'Himachal Pradesh': 'Himachal Pradesh',
        'Jharkhand': 'Jharkhand',
        'Karnataka': 'Karnataka',
        'Kerala': 'Kerala',
        'Madhya Pradesh': 'Madhya Pradesh',
        'Maharashtra': 'Maharashtra',
        'Manipur': 'Manipur',
        'Meghalaya': 'Meghalaya',
        'Mizoram': 'Mizoram',
        'Nagaland': 'Nagaland',
        'Odisha': 'Odisha',
        'Punjab': 'Punjab',
        'Rajasthan': 'Rajasthan',
        'Sikkim': 'Sikkim',
        'Tamil Nadu': 'Tamil Nadu',
        'Telangana': 'Telangana',
        'Tripura': 'Tripura',
        'Uttar Pradesh': 'Uttar Pradesh',
        'Uttarakhand': 'Uttarakhand',
        'West Bengal': 'West Bengal',
        'Delhi': 'Delhi',  # Exact match with GeoJSON
        'Jammu & Kashmir': 'Jammu & Kashmir',
        'Ladakh': 'Ladakh',
        'Puducherry': 'Puducherry',
        'Chandigarh': 'Chandigarh',
        # Key differences between CSV and GeoJSON:
        'Dadra & Nagar Haveli & Daman & Diu': 'Dadra and Nagar Haveli and Daman and Diu',  # & vs and
        'Andaman & Nicobar Islands': 'Andaman & Nicobar',  # Missing "Islands"
        'Lakshadweep': 'Lakshadweep'
    }


def create_simple_choropleth(df, value_col, title, color_scale='Viridis'):
    """
    Create a simple, reliable choropleth map of India.
    Focuses on functionality over fancy features.
    """
    import plotly.express as px
    import pandas as pd
    
    try:
        # Load GeoJSON and state mapping
        geojson_data = load_india_geojson()
        state_mapping = get_state_name_mapping()
        
        if not geojson_data.get('features'):
            return create_fallback_visualization(df, value_col, title, color_scale)
        
        # Prepare data
        plot_df = df.copy()
        plot_df['State_Normalized'] = plot_df['State'].map(state_mapping).fillna(plot_df['State'])
        plot_df = plot_df.dropna(subset=['State_Normalized'])
        
        if plot_df.empty:
            return create_fallback_visualization(df, value_col, title, color_scale)
        
        # Create simple choropleth
        fig = px.choropleth(
            plot_df,
            geojson=geojson_data,
            locations='State_Normalized',
            color=value_col,
            hover_name='State',
            color_continuous_scale=color_scale,
            title=title,
            featureidkey="properties.ST_NM"
        )
        
        # Simple layout updates
        fig.update_geos(fitbounds="locations", visible=False)
        fig.update_layout(height=600, title_x=0.5)
        
        return fig
        
    except Exception as e:
        print(f"Simple choropleth error: {str(e)}")
        return create_fallback_visualization(df, value_col, title, color_scale)


def create_enhanced_choropleth(df, value_col, title, color_scale='Viridis', show_scale=True):
    """
    Create an enhanced interactive choropleth map of India with proper GeoJSON integration.
    
    Args:
        df (pd.DataFrame): DataFrame with 'State' and value column
        value_col (str): Column name containing values to map
        title (str): Chart title
        color_scale (str): Plotly color scale (default: 'Viridis')
        show_scale (bool): Whether to show color scale bar
    
    Returns:
        plotly.graph_objects.Figure: Interactive choropleth map
    """
    import plotly.express as px
    import pandas as pd
    
    try:
        # Load GeoJSON and state mapping
        geojson_data = load_india_geojson()
        state_mapping = get_state_name_mapping()
        
        if not geojson_data.get('features'):
            st.warning("GeoJSON data not available. Using fallback visualization.")
            return create_fallback_visualization(df, value_col, title, color_scale)
        
        # Prepare data for choropleth
        plot_df = df.copy()
        
        # Normalize state names using mapping
        plot_df['State_Normalized'] = plot_df['State'].map(state_mapping)
        
        # Check for unmapped states and handle gracefully
        unmapped_states = plot_df[plot_df['State_Normalized'].isna()]['State'].unique()
        if len(unmapped_states) > 0:
            # Log unmapped states but don't clutter UI
            print(f"Warning: Unmapped states found: {list(unmapped_states)}")
            # Fill unmapped states with original names as fallback
            plot_df['State_Normalized'] = plot_df['State_Normalized'].fillna(plot_df['State'])
        
        # Remove rows with no state mapping
        plot_df = plot_df.dropna(subset=['State_Normalized'])
        
        if plot_df.empty:
            st.error("No valid state data after mapping. Using fallback visualization.")
            return create_fallback_visualization(df, value_col, title, color_scale)
        
        # Create choropleth map with correct featureidkey
        fig = px.choropleth(
            plot_df,
            geojson=geojson_data,
            locations='State_Normalized',
            color=value_col,
            hover_name='State',  # Use original state name for hover
            color_continuous_scale=color_scale,
            title=title,
            featureidkey="properties.ST_NM",  # Correct property key for India states GeoJSON
            labels={value_col: value_col.replace('_', ' ').title()}
        )
        
        # Customize layout for India with proper bounds
        fig.update_geos(
            projection_type="natural earth",
            showlakes=True,
            lakecolor='rgba(173, 216, 230, 0.3)',  # Light blue with transparency
            showocean=True,
            oceancolor='rgba(173, 216, 230, 0.1)',  # Very light blue
            showland=True,
            landcolor='rgba(243, 243, 243, 0.8)',  # Light gray for non-data areas
            fitbounds="locations",  # Fit to the data locations (India)
            visible=False  # Hide the default geographic features for cleaner look
        )
        
        # Update layout for better appearance
        fig.update_layout(
            height=600,
            title={
                'text': title,
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 16, 'family': 'Arial, sans-serif'}
            },
            coloraxis_showscale=show_scale,
            coloraxis_colorbar={
                'title': {'text': value_col.replace('_', ' ').title()},
                'thickness': 15,
                'len': 0.7,
                'x': 1.01,
                'xanchor': 'left'
            },
            margin={"r": 100, "t": 60, "l": 0, "b": 0},
            font={'family': 'Arial, sans-serif'}
        )
        
        # Enhanced hover templates
        if value_col == 'Transaction_Count':
            hover_template = '<b>%{hovertext}</b><br>Transactions: %{z:,.0f}<extra></extra>'
        elif value_col == 'Transaction_Amount':
            hover_template = '<b>%{hovertext}</b><br>Amount: ₹%{z:,.0f}<extra></extra>'
        elif value_col == 'Avg_Transaction_Value':
            hover_template = '<b>%{hovertext}</b><br>Avg Value: ₹%{z:,.2f}<extra></extra>'
        else:
            hover_template = '<b>%{hovertext}</b><br>Value: %{z:,.2f}<extra></extra>'
            
        fig.update_traces(
            hovertemplate=hover_template,
            marker_line_color='white',
            marker_line_width=0.5
        )
        
        return fig
        
    except Exception as e:
        import traceback
        error_msg = f"Choropleth map error: {str(e)}"
        full_traceback = traceback.format_exc()
        print(f"Choropleth Error Details: {error_msg}")
        print(f"Full traceback: {full_traceback}")
        st.error(f"Choropleth error: {error_msg}")
        st.warning("Map visualization temporarily unavailable. Showing alternative view.")
        return create_fallback_visualization(df, value_col, title, color_scale)


def create_fallback_visualization(df, value_col, title, color_scale='Viridis'):
    """
    Create enhanced fallback bar chart when choropleth fails.
    """
    import plotly.express as px
    
    # Sort by value for better visualization
    plot_df = df.sort_values(value_col, ascending=True).tail(20)  # Top 20 states
    
    fig = px.bar(
        plot_df,
        x=value_col,
        y='State',
        orientation='h',
        title=f"{title} (Top 20 States)",
        color=value_col,
        color_continuous_scale=color_scale,
        text=value_col
    )
    
    # Format text on bars
    if value_col == 'Transaction_Count':
        fig.update_traces(texttemplate='%{text:,.0f}', textposition='auto')
        hover_template = '<b>%{y}</b><br>Transactions: %{x:,.0f}<extra></extra>'
    elif value_col == 'Transaction_Amount':
        fig.update_traces(texttemplate='₹%{text:,.0f}', textposition='auto')
        hover_template = '<b>%{y}</b><br>Amount: ₹%{x:,.0f}<extra></extra>'
    else:
        fig.update_traces(texttemplate='%{text:,.2f}', textposition='auto')
        hover_template = '<b>%{y}</b><br>Value: %{x:,.2f}<extra></extra>'
    
    fig.update_traces(hovertemplate=hover_template)
    
    fig.update_layout(
        height=600,
        yaxis={'categoryorder': 'total ascending'},
        xaxis_title=value_col.replace('_', ' ').title(),
        yaxis_title='State',
        title={
            'x': 0.5,
            'xanchor': 'center'
        }
    )
    
    return fig


def create_transaction_type_filter_choropleth(df, selected_type=None):
    """
    Create choropleth with transaction type filtering capability.
    
    Args:
        df (pd.DataFrame): Transaction data
        selected_type (str): Selected transaction type filter
    
    Returns:
        plotly.graph_objects.Figure: Filtered choropleth map
    """
    if selected_type and selected_type != 'All Types':
        filtered_df = df[df['Transaction_Type'] == selected_type]
    else:
        filtered_df = df
    
    # Aggregate by state
    state_data = filtered_df.groupby('State').agg({
        'Transaction_Count': 'sum',
        'Transaction_Amount': 'sum'
    }).reset_index()
    
    # Calculate average transaction value
    state_data['Avg_Transaction_Value'] = (
        state_data['Transaction_Amount'] / state_data['Transaction_Count']
    ).fillna(0)
    
    return state_data


def test_state_mapping():
    """
    Test function to validate state name mapping between CSV and GeoJSON.
    Use this for debugging choropleth issues.
    """
    try:
        # Load actual data
        df = pd.read_csv('data/aggregated_transactions.csv') if 'data/aggregated_transactions.csv' else None
        if df is None:
            return "CSV data not available"
        
        # Get unique states from CSV
        csv_states = set(df['State'].unique())
        
        # Get state mapping
        mapping = get_state_name_mapping()
        
        # Get GeoJSON states
        geojson_data = load_india_geojson()
        if geojson_data.get('features'):
            geojson_states = set()
            for feature in geojson_data['features']:
                state_name = feature.get('properties', {}).get('ST_NM')
                if state_name:
                    geojson_states.add(state_name)
        else:
            geojson_states = set()
        
        # Analysis
        mapped_states = set(mapping.values())
        unmapped_csv = csv_states - set(mapping.keys())
        unmapped_geojson = geojson_states - mapped_states
        
        results = {
            'csv_states_count': len(csv_states),
            'geojson_states_count': len(geojson_states),
            'mapping_count': len(mapping),
            'unmapped_csv_states': list(unmapped_csv),
            'unmapped_geojson_states': list(unmapped_geojson),
            'mapping_success': len(unmapped_csv) == 0 and len(unmapped_geojson) == 0
        }
        
        return results
        
    except Exception as e:
        return f"Error in state mapping test: {str(e)}"


def test_choropleth_simple():
    """
    Simple test function to create a basic choropleth map.
    Returns success/failure status for debugging.
    """
    try:
        import plotly.express as px
        import pandas as pd
        
        # Create simple test data
        test_data = pd.DataFrame({
            'State': ['Maharashtra', 'Karnataka', 'Tamil Nadu', 'Gujarat', 'Uttar Pradesh'],
            'Value': [100, 80, 90, 75, 95]
        })
        
        # Try to load GeoJSON
        geojson_data = load_india_geojson()
        if not geojson_data.get('features'):
            return {'success': False, 'error': 'GeoJSON data not available'}
        
        # Apply state mapping
        mapping = get_state_name_mapping()
        test_data['State_Normalized'] = test_data['State'].map(mapping).fillna(test_data['State'])
        
        # Try to create choropleth
        fig = px.choropleth(
            test_data,
            geojson=geojson_data,
            locations='State_Normalized',
            color='Value',
            hover_name='State',
            featureidkey="properties.ST_NM",
            title="Test Choropleth"
        )
        
        return {'success': True, 'states_mapped': len(test_data), 'geojson_features': len(geojson_data['features'])}
        
    except Exception as e:
        import traceback
        return {
            'success': False, 
            'error': str(e),
            'traceback': traceback.format_exc()
        }


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
