import dash
from dash import dcc, html, dash_table, Input, Output, callback
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import dash_bootstrap_components as dbc
from datetime import datetime
import os
import glob

# Initialize the Dash app with modern theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME])
app.title = "SqueezeMetrics Financial Dashboard"

# Custom CSS for professional styling
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            .main-header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px 0;
                margin-bottom: 30px;
                border-radius: 10px;
            }
            .metric-card {
                transition: transform 0.2s;
            }
            .metric-card:hover {
                transform: translateY(-5px);
            }
            .nav-tabs .nav-link {
                color: #495057;
                font-weight: 500;
            }
            .nav-tabs .nav-link.active {
                background-color: #667eea;
                border-color: #667eea;
                color: white;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

def load_data():
    """Load the most recent SqueezeMetrics data file"""
    excel_files = glob.glob("squeeze_data_*.xlsx")
    if excel_files:
        # Get the most recent file
        latest_file = max(excel_files, key=os.path.getctime)
        df = pd.read_excel(latest_file)
        
        # Clean data thoroughly - same approach as simple dashboard
        df = df.dropna(subset=['TICKER', 'NAME'])  # Drop rows missing essential data
        
        # Fill NaN values with appropriate defaults
        fill_values = {
            'SECTOR': 'Unknown',
            'INDUSTRY': 'Unknown',
            'DATE': '2025-08-29',
            'P': 0, 'P_NORM': 0, 'V': 0, 'V_NORM': 0,
            'G': 0, 'G_NORM': 0, 'D': 0, 'D_NORM': 0,
            'IV': 0, 'IV_NORM': 0, 'P_NN': 0,
            'OPEN': 0, 'HIGH': 0, 'LOW': 0, 'CLOSE': 0,
            'VOLUME': 0, 'ADM21': 0, 'DAYS': 0
        }
        df = df.fillna(fill_values)
        
        # Ensure correct data types
        df['SECTOR'] = df['SECTOR'].astype(str)
        df['INDUSTRY'] = df['INDUSTRY'].astype(str)
        df['TICKER'] = df['TICKER'].astype(str)
        df['NAME'] = df['NAME'].astype(str)
        
        print(f"Loaded data from {latest_file}: {len(df)} records")
        return df
    else:
        print("No data files found. Please run fetch_squeeze_data.py first.")
        return pd.DataFrame()

# Load data
df = load_data()

# Create layout
def create_layout():
    if df.empty:
        return html.Div([
            dbc.Alert(
                "No data found. Please run fetch_squeeze_data.py to download data first.",
                color="warning"
            )
        ])
    
    return dbc.Container([
        # Header
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H1([
                        html.I(className="fas fa-chart-line me-3"),
                        "SqueezeMetrics Financial Dashboard"
                    ], className="text-center mb-3"),
                    html.P(f"Data as of {df['DATE'].iloc[0]} - {len(df)} securities", 
                           className="text-center mb-0")
                ], className="main-header text-center")
            ])
        ], className="mb-4"),
        
        # Filter Controls
        dbc.Row([
            dbc.Col([
                html.Label("Sector Filter:"),
                dcc.Dropdown(
                    id="sector-filter",
                    options=[{"label": "All Sectors", "value": "ALL"}] + 
                            [{"label": sector, "value": sector} for sector in sorted(df['SECTOR'].dropna().unique())],
                    value="ALL",
                    clearable=False
                )
            ], width=3),
            
            dbc.Col([
                html.Label("Industry Filter:"),
                dcc.Dropdown(
                    id="industry-filter",
                    options=[{"label": "All Industries", "value": "ALL"}],
                    value="ALL",
                    clearable=False
                )
            ], width=3),
            
            dbc.Col([
                html.Label("Min Volume:"),
                dcc.Input(
                    id="volume-filter",
                    type="number",
                    value=0,
                    min=0,
                    step=100000
                )
            ], width=2),
            
            dbc.Col([
                html.Label("Show Top N Records:"),
                dcc.Dropdown(
                    id="top-n-filter",
                    options=[
                        {"label": "25", "value": 25},
                        {"label": "50", "value": 50},
                        {"label": "100", "value": 100},
                        {"label": "All", "value": len(df)}
                    ],
                    value=50,
                    clearable=False
                )
            ], width=2),
            
            dbc.Col([
                dbc.Button("Refresh Data", id="refresh-btn", color="primary", className="mt-4"),
                html.Br(),
                dbc.Button("Export Filtered Data", id="export-btn", color="secondary", className="mt-2")
            ], width=2)
        ], className="mb-4"),
        
        # Main Content Tabs
        dcc.Tabs(id="main-tabs", value="overview", children=[
            dcc.Tab(label="Overview", value="overview"),
            dcc.Tab(label="Analysis", value="analysis"),
            dcc.Tab(label="Sector Comparison", value="sectors")
        ]),
        
        html.Div(id="tab-content")
        
    ], fluid=True)

app.layout = create_layout()

# Callback for updating industry filter based on sector
@app.callback(
    Output("industry-filter", "options"),
    Input("sector-filter", "value")
)
def update_industry_filter(selected_sector):
    if df.empty:
        return []
    
    if selected_sector == "ALL":
        industries = sorted(df['INDUSTRY'].dropna().unique())
    else:
        industries = sorted(df[df['SECTOR'] == selected_sector]['INDUSTRY'].dropna().unique())
    
    return [{"label": "All Industries", "value": "ALL"}] + [{"label": ind, "value": ind} for ind in industries]

# Callback for stock detail card
@app.callback(
    Output("stock-detail-card", "children"),
    Input("stock-selector", "value")
)
def update_stock_detail(selected_ticker):
    if not selected_ticker or df.empty:
        return html.Div()
    
    stock_data = df[df['TICKER'] == selected_ticker].iloc[0]
    
    # Create OHLC chart for the selected stock (single day data)
    ohlc_fig = go.Figure(data=go.Candlestick(
        x=[stock_data['DATE']],
        open=[stock_data['OPEN']],
        high=[stock_data['HIGH']],
        low=[stock_data['LOW']],
        close=[stock_data['CLOSE']]
    ))
    ohlc_fig.update_layout(
        title=f"{selected_ticker} - {stock_data['NAME']} OHLC",
        xaxis_title="Date",
        yaxis_title="Price ($)",
        height=300
    )
    
    # Stock metrics
    metrics_layout = dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("SqueezeMetrics Scores"),
                dbc.CardBody([
                    html.P(f"P Score: {stock_data['P']:.3f} (Norm: {stock_data['P_NORM']:.3f})", 
                           style={'fontWeight': 'bold' if abs(stock_data['P']) > 0.5 else 'normal'}),
                    html.P(f"P_NN (Neural Net): {stock_data['P_NN']:.4f}", 
                           style={'color': 'green' if stock_data['P_NN'] > 0 else 'red', 'fontWeight': 'bold'}),
                    html.P(f"V Score: {stock_data['V']:.3f} (Norm: {stock_data['V_NORM']:.3f})"),
                    html.P(f"G Score: {stock_data['G']:.3f} (Norm: {stock_data['G_NORM']:.3f})"),
                    html.P(f"D Score: {stock_data['D']:.3f} (Norm: {stock_data['D_NORM']:.3f})"),
                    html.P(f"IV: {stock_data['IV']:.2f} (Norm: {stock_data['IV_NORM']:.3f})")
                ])
            ])
        ], width=4),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Market Data"),
                dbc.CardBody([
                    html.P(f"Sector: {stock_data['SECTOR']}"),
                    html.P(f"Industry: {stock_data['INDUSTRY']}"),
                    html.P(f"Close: ${stock_data['CLOSE']:.2f}"),
                    html.P(f"Volume: {stock_data['VOLUME']:,.0f}"),
                    html.P(f"Days: {stock_data['DAYS']}")
                ])
            ])
        ], width=4),
        dbc.Col([
            dcc.Graph(figure=ohlc_fig)
        ], width=4)
    ])
    
    return metrics_layout

# Callback for data refresh
@app.callback(
    Output("refresh-btn", "children"),
    Input("refresh-btn", "n_clicks"),
    prevent_initial_call=True
)
def refresh_data(n_clicks):
    if n_clicks:
        global df
        df = load_data()
        return "Data Refreshed!"
    return "Refresh Data"

# Callback for export functionality
@app.callback(
    Output("export-btn", "children"),
    [Input("export-btn", "n_clicks"),
     Input("sector-filter", "value"),
     Input("industry-filter", "value"),
     Input("volume-filter", "value"),
     Input("top-n-filter", "value")],
    prevent_initial_call=True
)
def export_data(n_clicks, sector, industry, min_volume, top_n):
    if n_clicks:
        # Filter data same as in tab content
        filtered_df = df.copy()
        
        if sector != "ALL":
            filtered_df = filtered_df[filtered_df['SECTOR'] == sector]
        
        if industry != "ALL":
            filtered_df = filtered_df[filtered_df['INDUSTRY'] == industry]
        
        if min_volume > 0:
            filtered_df = filtered_df[filtered_df['VOLUME'] >= min_volume]
        
        filtered_df = filtered_df.head(top_n)
        
        # Export to CSV
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"filtered_squeeze_data_{timestamp}.csv"
        filtered_df.to_csv(filename, index=False)
        
        return f"Exported! ({len(filtered_df)} rows)"
    return "Export Filtered Data"

# Callback for tab content
@app.callback(
    Output("tab-content", "children"),
    [Input("main-tabs", "value"),
     Input("sector-filter", "value"),
     Input("industry-filter", "value"),
     Input("volume-filter", "value"),
     Input("top-n-filter", "value")]
)
def render_tab_content(active_tab, sector, industry, min_volume, top_n):
    if df.empty:
        return html.Div("No data available")
    
    # Filter data
    filtered_df = df.copy()
    
    if sector != "ALL":
        filtered_df = filtered_df[filtered_df['SECTOR'] == sector]
    
    if industry != "ALL":
        filtered_df = filtered_df[filtered_df['INDUSTRY'] == industry]
    
    if min_volume > 0:
        filtered_df = filtered_df[filtered_df['VOLUME'] >= min_volume]
    
    # Limit to top N records
    filtered_df = filtered_df.head(top_n)
    
    if active_tab == "overview":
        return create_overview_tab(filtered_df)
    elif active_tab == "analysis":
        return create_analysis_tab(filtered_df)
    elif active_tab == "sectors":
        return create_sectors_tab(df)  # Use full dataset for sector comparison

def create_overview_tab(filtered_df):
    """Create the overview tab with data table and key metrics"""
    
    # Handle empty dataframe
    if filtered_df.empty:
        return html.Div([
            dbc.Alert("No data matches the current filters. Please adjust your filters.", color="warning")
        ])
    
    # Key metrics cards
    metrics_cards = dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.I(className="fas fa-list-alt fa-2x text-primary mb-2"),
                        html.H4(f"{len(filtered_df):,}", className="card-title mb-0"),
                        html.P("Securities", className="card-text text-muted")
                    ], className="text-center")
                ])
            ], className="metric-card shadow-sm")
        ], width=2),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.I(className="fas fa-volume-up fa-2x text-success mb-2"),
                        html.H4(f"{filtered_df['VOLUME'].sum():,.0f}", className="card-title mb-0"),
                        html.P("Total Volume", className="card-text text-muted")
                    ], className="text-center")
                ])
            ], className="metric-card shadow-sm")
        ], width=2),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.I(className="fas fa-chart-bar fa-2x text-info mb-2"),
                        html.H4(f"{filtered_df['P'].mean():.3f}", className="card-title mb-0"),
                        html.P("Avg P Score", className="card-text text-muted")
                    ], className="text-center")
                ])
            ], className="metric-card shadow-sm")
        ], width=2),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.I(className="fas fa-chart-area fa-2x text-warning mb-2"),
                        html.H4(f"{filtered_df['V'].mean():.3f}", className="card-title mb-0"),
                        html.P("Avg V Score", className="card-text text-muted")
                    ], className="text-center")
                ])
            ], className="metric-card shadow-sm")
        ], width=2),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.I(className="fas fa-arrow-up fa-2x text-danger mb-2"),
                        html.H4(f"{filtered_df['G'].mean():.3f}", className="card-title mb-0"),
                        html.P("Avg G Score", className="card-text text-muted")
                    ], className="text-center")
                ])
            ], className="metric-card shadow-sm")
        ], width=2),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.I(className="fas fa-arrow-down fa-2x text-secondary mb-2"),
                        html.H4(f"{filtered_df['D'].mean():.3f}", className="card-title mb-0"),
                        html.P("Avg D Score", className="card-text text-muted")
                    ], className="text-center")
                ])
            ], className="metric-card shadow-sm")
        ], width=2)
    ], className="mb-3"),
    
    # Second row of metrics with P_NN
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.I(className="fas fa-brain fa-2x text-purple mb-2"),
                        html.H4(f"{filtered_df['P_NN'].mean():.4f}", className="card-title mb-0"),
                        html.P("Avg P_NN (Neural Net)", className="card-text text-muted")
                    ], className="text-center")
                ])
            ], className="metric-card shadow-sm")
        ], width=2),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.I(className="fas fa-chart-line fa-2x text-success mb-2"),
                        html.H4(f"{len(filtered_df[filtered_df['P_NN'] > 0]):,}", className="card-title mb-0"),
                        html.P("Positive P_NN", className="card-text text-muted")
                    ], className="text-center")
                ])
            ], className="metric-card shadow-sm")
        ], width=2),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.I(className="fas fa-percentage fa-2x text-info mb-2"),
                        html.H4(f"{(len(filtered_df[filtered_df['P_NN'] > 0]) / max(len(filtered_df), 1) * 100):.1f}%", className="card-title mb-0"),
                        html.P("P_NN Success Rate", className="card-text text-muted")
                    ], className="text-center")
                ])
            ], className="metric-card shadow-sm")
        ], width=2),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.I(className="fas fa-arrow-up fa-2x text-success mb-2"),
                        html.H4(f"{filtered_df['P_NN'].max():.4f}", className="card-title mb-0"),
                        html.P("Max P_NN", className="card-text text-muted")
                    ], className="text-center")
                ])
            ], className="metric-card shadow-sm")
        ], width=2),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.I(className="fas fa-arrow-down fa-2x text-danger mb-2"),
                        html.H4(f"{filtered_df['P_NN'].min():.4f}", className="card-title mb-0"),
                        html.P("Min P_NN", className="card-text text-muted")
                    ], className="text-center")
                ])
            ], className="metric-card shadow-sm")
        ], width=2)
    ], className="mb-4")
    
    # Data table
    data_table = dash_table.DataTable(
        id="main-data-table",
        data=filtered_df.to_dict('records'),
        columns=[
            {"name": "Ticker", "id": "TICKER", "type": "text"},
            {"name": "Name", "id": "NAME", "type": "text"},
            {"name": "Sector", "id": "SECTOR", "type": "text"},
            {"name": "Industry", "id": "INDUSTRY", "type": "text"},
            {"name": "P", "id": "P", "type": "numeric", "format": {"specifier": ".3f"}},
            {"name": "P_NN", "id": "P_NN", "type": "numeric", "format": {"specifier": ".4f"}},
            {"name": "V", "id": "V", "type": "numeric", "format": {"specifier": ".3f"}},
            {"name": "G", "id": "G", "type": "numeric", "format": {"specifier": ".3f"}},
            {"name": "D", "id": "D", "type": "numeric", "format": {"specifier": ".3f"}},
            {"name": "IV", "id": "IV", "type": "numeric", "format": {"specifier": ".2f"}},
            {"name": "Close", "id": "CLOSE", "type": "numeric", "format": {"specifier": "$.2f"}},
            {"name": "Volume", "id": "VOLUME", "type": "numeric", "format": {"specifier": ",.0f"}},
        ],
        sort_action="native",
        filter_action="native",
        page_action="native",
        page_current=0,
        page_size=15,
        style_cell={'textAlign': 'left', 'fontSize': 12},
        style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'},
        style_data_conditional=[
            {
                'if': {'filter_query': '{P} > 0.5'},
                'backgroundColor': '#d4edda',
                'color': 'black',
            },
            {
                'if': {'filter_query': '{P} < -0.5'},
                'backgroundColor': '#f8d7da',
                'color': 'black',
            }
        ]
    )
    
    return html.Div([
        metrics_cards,
        html.H4("Securities Data Table"),
        data_table
    ])

def create_analysis_tab(filtered_df):
    """Create the analysis tab with charts"""
    
    # Handle empty dataframe
    if filtered_df.empty:
        return html.Div([
            dbc.Alert("No data matches the current filters. Please adjust your filters.", color="warning")
        ])
    
    # Stock selector
    stock_selector = html.Div([
        html.Label("Select Stock for Detailed Analysis:"),
        dcc.Dropdown(
            id="stock-selector",
            options=[{"label": f"{row['TICKER']} - {row['NAME']}", "value": row['TICKER']} 
                    for _, row in filtered_df.iterrows()],
            value=filtered_df.iloc[0]['TICKER'] if not filtered_df.empty else None,
            clearable=False
        )
    ], className="mb-4")
    
    # P vs V scatter plot
    pv_scatter = dcc.Graph(
        id="pv-scatter",
        figure=px.scatter(
            filtered_df, 
            x='P', y='V', 
            color='SECTOR',
            size='VOLUME',
            hover_data=['TICKER', 'NAME', 'CLOSE'],
            title="P Score vs V Score by Sector (Size = Volume)"
        )
    )
    
    # G vs D scatter plot  
    gd_scatter = dcc.Graph(
        id="gd-scatter",
        figure=px.scatter(
            filtered_df, 
            x='G', y='D', 
            color='SECTOR',
            size='VOLUME',
            hover_data=['TICKER', 'NAME', 'CLOSE'],
            title="G Score vs D Score by Sector (Size = Volume)"
        )
    )
    
    # P_NN vs P scatter (Neural Net vs Traditional)
    p_nn_scatter = dcc.Graph(
        figure=px.scatter(
            filtered_df,
            x='P', y='P_NN',
            color='SECTOR',
            size='VOLUME',
            hover_data=['TICKER', 'NAME', 'CLOSE'],
            title="P_NN (Neural Net) vs P Score - Key Predictor Analysis"
        )
    )
    
    # IV vs Volume scatter
    iv_volume_scatter = dcc.Graph(
        figure=px.scatter(
            filtered_df,
            x='IV', y='VOLUME',
            color='SECTOR',
            hover_data=['TICKER', 'NAME', 'CLOSE', 'P_NN'],
            title="Implied Volatility vs Volume by Sector"
        )
    )
    
    # Selected stock detail card
    stock_detail = html.Div(id="stock-detail-card")
    
    return html.Div([
        stock_selector,
        stock_detail,
        dbc.Row([
            dbc.Col([pv_scatter], width=6),
            dbc.Col([gd_scatter], width=6)
        ]),
        dbc.Row([
            dbc.Col([p_nn_scatter], width=6),
            dbc.Col([iv_volume_scatter], width=6)
        ])
    ])

def create_sectors_tab(full_df):
    """Create the sector comparison tab"""
    
    # Sector performance summary
    sector_summary = full_df.groupby('SECTOR').agg({
        'P': 'mean',
        'P_NN': 'mean',
        'V': 'mean', 
        'G': 'mean',
        'D': 'mean',
        'IV': 'mean',
        'VOLUME': 'sum',
        'TICKER': 'count'
    }).round(4)
    sector_summary.columns = ['Avg_P', 'Avg_P_NN', 'Avg_V', 'Avg_G', 'Avg_D', 'Avg_IV', 'Total_Volume', 'Count']
    sector_summary = sector_summary.reset_index()
    
    # Sector heatmap including P_NN
    heatmap_fig = go.Figure(data=go.Heatmap(
        z=[sector_summary['Avg_P'], sector_summary['Avg_P_NN'], sector_summary['Avg_V'], 
           sector_summary['Avg_G'], sector_summary['Avg_D']],
        x=sector_summary['SECTOR'],
        y=['P Score', 'P_NN (Neural Net)', 'V Score', 'G Score', 'D Score'],
        colorscale='RdYlGn',
        colorbar=dict(title="Score Value")
    ))
    heatmap_fig.update_layout(
        title="Sector Performance Heatmap - Including P_NN Neural Network Predictions",
        height=400
    )
    
    sector_heatmap = dcc.Graph(figure=heatmap_fig)
    
    # Sector summary table
    sector_table = dash_table.DataTable(
        data=sector_summary.to_dict('records'),
        columns=[{"name": i, "id": i, "type": "numeric" if i != "SECTOR" else "text"} for i in sector_summary.columns],
        sort_action="native",
        style_cell={'textAlign': 'left'},
        style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'}
    )
    
    return html.Div([
        html.H4("Sector Performance Summary"),
        sector_table,
        html.Br(),
        sector_heatmap
    ])

if __name__ == "__main__":
    app.run(debug=True, port=8051, host='127.0.0.1')