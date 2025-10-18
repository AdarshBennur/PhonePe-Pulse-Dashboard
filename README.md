# 📱 PhonePe Pulse Dashboard

A comprehensive, interactive Streamlit dashboard for analyzing PhonePe's digital payment ecosystem across India. This multi-page application provides deep insights into transaction patterns, user behavior, insurance trends, and geographic distributions.

## 🎯 Features

### 🏠 Home Page
- **Welcome Overview**: Quick stats and navigation guide
- **Key Metrics**: Total transactions, users, insurance policies, and values
- **Quick Insights**: Transaction distribution and top-performing states
- **Recent Trends**: Latest quarterly patterns

### 📊 Overview Page  
- **Geographic Analytics**: State-wise transaction heatmaps
- **Distribution Analysis**: Transaction type breakdowns with interactive donut charts
- **Performance Comparison**: State performance matrices and correlations
- **District Analysis**: Top-performing districts and regions

### 💳 Transactions Page
- **Detailed Filtering**: State, year, quarter, and transaction type filters
- **Trend Analysis**: Time-series visualization of transaction patterns
- **Type Breakdown**: Comprehensive analysis by transaction categories
- **Growth Insights**: Period-over-period growth calculations

### 👥 Users Page
- **User Analytics**: Registration trends and app engagement metrics
- **Geographic Distribution**: User adoption patterns across states
- **Behavior Analysis**: App opens per user and usage intensity
- **Segmentation**: User segments based on adoption and engagement

### 🛡️ Insurance Page
- **Regional Analysis**: Insurance adoption patterns by geography
- **Temporal Trends**: Insurance growth and seasonal patterns
- **Penetration Analysis**: Insurance penetration rates across states
- **Value Analysis**: Policy values and market concentration

### 📈 Trends & Comparison Page
- **Comprehensive Trends**: Multi-metric time-series analysis
- **State Comparisons**: Side-by-side state performance comparison
- **Correlation Analysis**: Cross-metric relationship insights
- **Growth Analysis**: Detailed growth rate calculations

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation & Setup

1. **Clone or Download**: Ensure you have all the project files in your directory

2. **Create Virtual Environment** (Recommended):
   ```bash
   # Create virtual environment
   python3 -m venv venv
   
   # Activate on macOS/Linux
   source venv/bin/activate
   
   # Activate on Windows
   venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   
   **Core Dependencies:**
   - `streamlit>=1.28.0` - Web framework
   - `plotly>=5.15.0` - Interactive visualizations
   - `pandas>=1.5.0` - Data processing
   - `numpy>=1.21.0` - Numerical computing

4. **Verify Data Structure**: Ensure your `/data` folder contains all required CSV files:
   ```
   data/
   ├── aggregated_transactions.csv
   ├── aggregated_users.csv
   ├── aggregated_insurance.csv
   ├── map_transactions.csv
   └── top_performers.csv
   ```

5. **Run the Application**:
   ```bash
   streamlit run 🏠_Home.py
   ```
   
   **Note:** Always run the application from the project root directory to ensure proper file path resolution.

6. **Access Dashboard**: Open your browser and navigate to `http://localhost:8501`

## 📁 Project Structure

```
PhonePe Pulse Dashboard/
├── 🏠_Home.py                  # Main application entry point
├── requirements.txt            # Python dependencies
├── README.md                  # This file
├── data/                      # Data directory (CSV files)
│   ├── aggregated_transactions.csv
│   ├── aggregated_users.csv
│   ├── aggregated_insurance.csv
│   ├── map_transactions.csv
│   └── top_performers.csv
├── utils/                     # Utility functions
│   └── data_loader.py        # Data loading and processing utilities
└── pages/                     # Streamlit pages
    ├── 1_📊_Overview.py      # Geographic and distribution analytics
    ├── 2_💳_Transactions.py  # Transaction analysis
    ├── 3_👥_Users.py         # User analytics
    ├── 4_🛡️_Insurance.py     # Insurance insights
    └── 5_📈_Trends.py        # Trends and comparative analysis
```

## 🔧 Configuration & Customization

### Data Requirements
The dashboard expects CSV files with the following structure:

**aggregated_transactions.csv**:
- State, Year, Quarter, Transaction_Type, Transaction_Count, Transaction_Amount

**aggregated_users.csv**:
- State, Year, Quarter, Registered_Users, App_Opens

**aggregated_insurance.csv**:
- State, Year, Quarter, Insurance_Type, Insurance_Count, Insurance_Amount

**map_transactions.csv**:
- State, Year, Quarter, District, Transaction_Count, Transaction_Amount

**top_performers.csv**:
- State, Year, Quarter, Type, Name, Transaction_Count, Transaction_Amount

### Customization Options

1. **Add New Visualizations**: 
   - Modify page files in `/pages` directory
   - Use plotly for interactive charts
   - Follow existing patterns for consistency

2. **Update Styling**:
   - Modify CSS in individual page files
   - Update color schemes and themes
   - Add custom Streamlit components

3. **Extend Functionality**:
   - Add new utility functions in `/utils/data_loader.py`
   - Implement additional filters and metrics
   - Create new analysis pages

## 📊 Key Technologies

- **Frontend**: Streamlit (Interactive web framework)
- **Visualization**: Plotly (Interactive charts and graphs)
- **Data Processing**: Pandas, NumPy
- **Styling**: Custom CSS with Streamlit theming
- **Architecture**: Multi-page app with modular design

## 🎛️ Usage Tips

### Navigation
- Use the sidebar to navigate between different analysis sections
- Each page has independent filters for focused analysis
- All visualizations are interactive - hover, zoom, and click for details

### Filtering
- Apply filters to drill down into specific time periods, states, or transaction types
- Filters are persistent within each page session
- Clear filters by refreshing the page or selecting "All" options

### Export & Sharing
- Use Streamlit's built-in screenshot functionality
- Charts can be downloaded as PNG files via plotly controls
- Share the dashboard URL for collaborative analysis

## 🚦 Performance Optimization

The dashboard includes several performance optimizations:

- **Data Caching**: `@st.cache_data` for expensive operations
- **Efficient Loading**: PyArrow for faster CSV processing
- **Modular Design**: Separate utility functions for reusability
- **Optimized Queries**: Pandas operations optimized for large datasets

## 🛠️ Troubleshooting

### Common Issues

1. **Import Errors** (`ModuleNotFoundError` or `reportMissingImports`):
   - **Solution 1:** Ensure virtual environment is activated before running
   - **Solution 2:** Install all dependencies: `pip install -r requirements.txt`
   - **Solution 3 (VSCode):** Select correct Python interpreter:
     - Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows)
     - Type "Python: Select Interpreter"
     - Choose the interpreter from your `venv` folder
   - **Solution 4:** The `.vscode/settings.json` file is included to help with import resolution
   - **Solution 5:** Always run from project root: `cd "/Users/adarsh/Labmentix/2. PhonePe"` before running streamlit

2. **File Not Found Error** (`Home.py not found`):
   - The actual filename is `🏠_Home.py` (with emoji)
   - Run: `streamlit run 🏠_Home.py` (not `Home.py`)
   - Always run from the project root directory

3. **Data Loading Errors**:
   - Verify CSV files are in the correct `/data` directory
   - Check file formats match expected structure
   - Ensure all required columns are present
   - The app uses absolute paths based on project structure, so it should work from anywhere

4. **Performance Issues**:
   - Clear Streamlit cache: `streamlit cache clear`
   - Reduce data size if working with very large datasets
   - Check available system memory

5. **Visualization Problems**:
   - Update plotly: `pip install --upgrade plotly`
   - Clear browser cache
   - Try different browser if issues persist

### Support & Development

For technical support or feature requests:
1. Check the error messages in the Streamlit interface
2. Review the console output for detailed error information
3. Verify all dependencies are correctly installed
4. Test with sample data to isolate issues

## 📈 Future Enhancements

Potential areas for expansion:
- Real-time data integration
- Machine learning predictions
- Advanced statistical analysis
- Export functionality for reports
- Mobile-responsive optimizations
- Additional geographic visualizations (choropleth maps)

## 🎉 Getting Started Checklist

- [ ] Python 3.8+ installed
- [ ] Virtual environment created and activated (`python3 -m venv venv && source venv/bin/activate`)
- [ ] All CSV files in `/data` directory
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] No import warnings in your IDE (if using VSCode, ensure correct interpreter is selected)
- [ ] Application running from project root (`streamlit run 🏠_Home.py`)
- [ ] Dashboard accessible in browser at `http://localhost:8501`
- [ ] All pages loading without errors

## 📞 Contact & Support

This dashboard provides a comprehensive view of PhonePe's digital ecosystem. For optimal experience:
- Use a modern web browser (Chrome, Firefox, Safari)
- Ensure stable internet connection for initial loading
- Allow time for data processing on first run

---

**Built with ❤️ using Streamlit, Plotly, and Python**

*Ready for immediate launch and production use*
