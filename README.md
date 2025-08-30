# SqueezeMetrics Financial Dashboard

A professional Plotly Dash dashboard for analyzing SqueezeMetrics financial data across 5,000+ securities.

## Features

### 📊 **Overview Tab**
- **Interactive Data Table**: Sort, filter, and search through securities data
- **Key Metrics Cards**: Real-time statistics with hover animations
- **Smart Filtering**: Sector, industry, volume, and record count filters
- **Conditional Formatting**: Color-coded P scores (green for positive, red for negative)

### 📈 **Analysis Tab**
- **Individual Stock Analysis**: Select any security for detailed view
- **OHLC Candlestick Charts**: Single-day OHLC visualization
- **Interactive Scatter Plots**: 
  - P vs V scores with sector coloring and volume sizing
  - G vs D scores with sector coloring and volume sizing
  - IV vs Volume analysis
- **Stock Detail Cards**: Complete SqueezeMetrics and market data

### 🏢 **Sector Comparison Tab**
- **Sector Summary Table**: Aggregated metrics by sector
- **Performance Heatmap**: Visual comparison of P, V, G, D scores across sectors

### ⚡ **Advanced Features**
- **Real-time Data Refresh**: Update data without restarting
- **Export Functionality**: Export filtered data to CSV
- **Professional Styling**: Modern gradient design with Font Awesome icons
- **Responsive Design**: Works on desktop and mobile devices

## Installation

1. **Install Dependencies**:
   ```bash
   pip install dash dash-table plotly dash-bootstrap-components pandas requests openpyxl
   ```

2. **Download Data**:
   ```bash
   python fetch_squeeze_data.py
   ```

3. **Run Dashboard**:
   ```bash
   python dashboard.py
   ```

4. **Open Browser**: Navigate to `http://127.0.0.1:8050`

## Data Structure

The dashboard analyzes 23 columns of data per security:

### Basic Information
- **TICKER**: Stock symbol
- **NAME**: Company name  
- **SECTOR**: Business sector
- **INDUSTRY**: Specific industry
- **DATE**: Data date

### SqueezeMetrics Scores
- **P, P_NORM**: Put/Call ratio and normalized score
- **V, V_NORM**: Volume ratio and normalized score
- **G, G_NORM**: Gamma exposure and normalized score
- **D, D_NORM**: Delta exposure and normalized score
- **IV, IV_NORM**: Implied volatility and normalized score
- **P_NN**: Neural network P score

### Market Data
- **OPEN, HIGH, LOW, CLOSE**: OHLC prices
- **VOLUME**: Trading volume
- **ADM21**: 21-day average dollar volume
- **DAYS**: Days since IPO

## Usage Guide

### Filtering Data
1. **Sector Filter**: Choose specific sectors or "All Sectors"
2. **Industry Filter**: Automatically updates based on sector selection
3. **Volume Filter**: Set minimum volume threshold
4. **Top N Filter**: Limit results to top 25, 50, 100, or all records

### Analyzing Individual Stocks
1. Switch to **Analysis** tab
2. Use **Stock Selector** dropdown to choose a security
3. View detailed metrics and OHLC chart
4. Analyze position in scatter plots

### Comparing Sectors
1. Switch to **Sector Comparison** tab
2. Review sector summary statistics
3. Analyze performance heatmap for visual comparison

### Exporting Data
1. Apply desired filters
2. Click **Export Filtered Data** button
3. Find CSV file in project directory with timestamp

### Refreshing Data
1. Run `python fetch_squeeze_data.py` to get latest data
2. Click **Refresh Data** button in dashboard
3. Or restart dashboard application

## Performance Features

- **Pagination**: Data table shows 15 rows per page
- **Client-side Filtering**: Fast table interactions
- **Lazy Loading**: Efficient handling of 5K+ records
- **Responsive Charts**: Automatic resizing and mobile support

## Customization

### Styling
- Modify CSS in `app.index_string` for custom themes
- Update Bootstrap theme in `external_stylesheets`
- Adjust card colors and animations

### Metrics
- Add new calculated columns in data processing
- Create additional visualization types
- Extend sector analysis capabilities

## File Structure

```
Squeeze/
├── dashboard.py              # Main dashboard application
├── fetch_squeeze_data.py     # Data fetching script
├── squeeze_data_*.xlsx       # Data files
├── IMPLEMENTATION_PLAN.md    # Development roadmap
├── README.md                 # This file
└── filtered_squeeze_data_*.csv  # Exported data files
```

## Troubleshooting

### Common Issues

1. **No Data Found**: Run `fetch_squeeze_data.py` first
2. **Port Already in Use**: Change port in `app.run(port=8051)`
3. **Missing Dependencies**: Install all packages from requirements above
4. **Slow Performance**: Reduce `top_n_filter` value for faster loading

### Error Messages

- **"No data files found"**: Download data using fetch script
- **"Module not found"**: Install missing Python packages
- **Charts not displaying**: Check browser console for JavaScript errors

## Future Enhancements

- Historical data integration for multi-day trends
- Advanced filtering with custom formulas
- Automated alerts for significant score changes  
- Portfolio tracking and analysis features
- Integration with additional financial APIs

## Support

For issues and feature requests, check the implementation plan and modify the dashboard code accordingly. The modular design makes it easy to add new visualizations and features.