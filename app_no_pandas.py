import os
import csv
import dash
from dash import dcc, html, dash_table, Input, Output, callback
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import requests
from datetime import datetime
from io import StringIO

# Production app configuration
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "SqueezeMetrics Financial Dashboard"
server = app.server  # This is required for Render

# Load data function for production (fetches from API)
def load_data_from_api():
    """
    Fetches latest data from SqueezeMetrics API - NO PANDAS VERSION
    """
    api_url = "https://squeezemetrics.com/monitor/api/latest?format=csv&key=0B7661B124724CA4C43BED7742F01266945A7B04BF698A758C9101727FE7392D"
    
    try:
        response = requests.get(api_url, timeout=30)
        response.raise_for_status()
        
        # Parse CSV manually without pandas
        csv_data = StringIO(response.text)
        reader = csv.DictReader(csv_data)
        data = []
        
        numeric_cols = ['P', 'P_NN', 'V', 'G', 'D', 'IV', 'CLOSE', 'VOLUME', 'OPEN', 'HIGH', 'LOW', 'P_NORM', 'V_NORM', 'G_NORM', 'D_NORM', 'IV_NORM']
        
        for row in reader:
            # Skip rows without ticker
            if not row.get('TICKER'):
                continue
                
            # Clean numeric columns
            for col in numeric_cols:
                if col in row:
                    try:
                        row[col] = float(row[col]) if row[col] and row[col] != 'NaN' else 0.0
                    except (ValueError, TypeError):
                        row[col] = 0.0
            
            # Fill missing values
            for key, value in row.items():
                if value == '' or value == 'NaN':
                    row[key] = 'Unknown' if key in ['NAME', 'SECTOR', 'INDUSTRY'] else 0.0
            
            data.append(row)
        
        print(f"Loaded {len(data)} clean records from API")
        return data
        
    except Exception as e:
        print(f"Error loading data from API: {e}")
        # Return empty data if API fails
        return []

# Load data
data = load_data_from_api()

# Get unique values for filters (manual approach)
def get_unique_values(data, column):
    values = set()
    for row in data:
        if row.get(column) and row[column] != 'Unknown':
            values.add(row[column])
    return sorted(list(values))

sectors = get_unique_values(data, 'SECTOR')
industries = get_unique_values(data, 'INDUSTRY')

# Enhanced layout with professional styling
app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H1("SqueezeMetrics Financial Dashboard", className="text-center text-white mb-2"),
                html.P(f"Analyzing {len(data)} securities with P_NN neural network predictions", className="text-center text-white-50"),
                html.P("🔴 LIVE DATA from SqueezeMetrics API", className="text-center text-white-50 mb-0")
            ], style={
                'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                'padding': '30px',
                'borderRadius': '10px',
                'marginBottom': '30px'
            })
        ])
    ]),
    
    # Control Panel
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Filters & Controls"),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label("Sector Filter:", className="fw-bold"),
                            dcc.Dropdown(
                                id="sector-filter",
                                options=[{"label": "All Sectors", "value": "All"}] + 
                                        [{"label": sector, "value": sector} for sector in sectors],
                                value="All",
                                clearable=False
                            )
                        ], width=6),
                        dbc.Col([
                            html.Label("Min P_NN Value:", className="fw-bold"),
                            dcc.Input(
                                id="pnn-filter",
                                type="number",
                                value=0,
                                step=0.01,
                                placeholder="Filter by P_NN..."
                            )
                        ], width=6),
                    ])
                ])
            ])
        ])
    ], className="mb-4"),
    
    # Tabs
    dcc.Tabs(id="tabs", value="overview", children=[
        dcc.Tab(label="📊 Overview", value="overview"),
        dcc.Tab(label="💼 Portfolio", value="portfolio"),
        dcc.Tab(label="📈 Analysis", value="analysis")
    ]),
    
    html.Div(id="tab-content")
])

# Callback for tab content
@app.callback(
    Output("tab-content", "children"),
    [Input("tabs", "value"),
     Input("sector-filter", "value"),
     Input("pnn-filter", "value")]
)
def update_tab_content(tab, sector_filter, pnn_filter):
    # Filter data
    filtered_data = data.copy()
    
    if sector_filter and sector_filter != "All":
        filtered_data = [row for row in filtered_data if row.get('SECTOR') == sector_filter]
    
    if pnn_filter and pnn_filter != 0:
        filtered_data = [row for row in filtered_data if float(row.get('P_NN', 0)) >= pnn_filter]
    
    if tab == "overview":
        return html.Div([
            html.H3("📊 Securities Overview", className="mt-3 mb-3"),
            html.P(f"Showing {len(filtered_data)} securities", className="text-muted"),
            dash_table.DataTable(
                data=filtered_data[:100],  # Limit to first 100 rows
                columns=[
                    {'name': 'Ticker', 'id': 'TICKER'},
                    {'name': 'Name', 'id': 'NAME'}, 
                    {'name': 'Sector', 'id': 'SECTOR'},
                    {'name': 'P_NN 🧠', 'id': 'P_NN', 'type': 'numeric', 'format': {'specifier': '.4f'}},
                    {'name': 'Close', 'id': 'CLOSE', 'type': 'numeric', 'format': {'specifier': '$.2f'}},
                    {'name': 'Volume', 'id': 'VOLUME', 'type': 'numeric', 'format': {'specifier': ',.0f'}}
                ],
                sort_action="native",
                page_size=50,
                style_cell={'textAlign': 'left'},
                style_data_conditional=[
                    {
                        'if': {'filter_query': '{P_NN} > 0.1'},
                        'backgroundColor': '#d4edda',
                        'color': 'black',
                    },
                    {
                        'if': {'filter_query': '{P_NN} < -0.1'},
                        'backgroundColor': '#f8d7da',
                        'color': 'black',
                    }
                ]
            )
        ])
    
    elif tab == "portfolio":
        # Simple portfolio construction without pandas
        portfolio_universe = [row for row in filtered_data 
                             if float(row.get('VOLUME', 0)) >= 10_000_000 and row.get('INDUSTRY') != 'ETF']
        
        # Sort by P_NN manually
        portfolio_universe.sort(key=lambda x: float(x.get('P_NN', 0)), reverse=True)
        
        # Take top 20 and bottom 20
        long_positions = portfolio_universe[:20]
        short_positions = portfolio_universe[-20:]
        
        return html.Div([
            html.H3("💼 Portfolio Builder", className="mt-3 mb-3"),
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Long Positions (Top 20)"),
                        dbc.CardBody([
                            dash_table.DataTable(
                                data=long_positions,
                                columns=[
                                    {'name': 'Ticker', 'id': 'TICKER'},
                                    {'name': 'Name', 'id': 'NAME'},
                                    {'name': 'P_NN', 'id': 'P_NN', 'type': 'numeric', 'format': {'specifier': '.4f'}},
                                    {'name': 'Close', 'id': 'CLOSE', 'type': 'numeric', 'format': {'specifier': '$.2f'}}
                                ],
                                style_header={'backgroundColor': '#28a745', 'color': 'white'},
                                page_size=20
                            )
                        ])
                    ])
                ], width=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Short Positions (Bottom 20)"),
                        dbc.CardBody([
                            dash_table.DataTable(
                                data=short_positions,
                                columns=[
                                    {'name': 'Ticker', 'id': 'TICKER'},
                                    {'name': 'Name', 'id': 'NAME'},
                                    {'name': 'P_NN', 'id': 'P_NN', 'type': 'numeric', 'format': {'specifier': '.4f'}},
                                    {'name': 'Close', 'id': 'CLOSE', 'type': 'numeric', 'format': {'specifier': '$.2f'}}
                                ],
                                style_header={'backgroundColor': '#dc3545', 'color': 'white'},
                                page_size=20
                            )
                        ])
                    ])
                ], width=6)
            ])
        ])
    
    elif tab == "analysis":
        # Simple scatter plot without pandas
        if len(filtered_data) > 0:
            x_vals = [float(row.get('P', 0)) for row in filtered_data[:200]]  # Limit for performance
            y_vals = [float(row.get('P_NN', 0)) for row in filtered_data[:200]]
            tickers = [row.get('TICKER', '') for row in filtered_data[:200]]
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=x_vals,
                y=y_vals,
                mode='markers',
                text=tickers,
                hovertemplate='<b>%{text}</b><br>P: %{x}<br>P_NN: %{y}<extra></extra>'
            ))
            fig.update_layout(title="P vs P_NN Scatter Plot", xaxis_title="P Score", yaxis_title="P_NN Neural Network")
            
            return html.Div([
                html.H3("📈 Analysis", className="mt-3 mb-3"),
                dcc.Graph(figure=fig)
            ])
        else:
            return html.Div([html.P("No data available for analysis")])

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run_server(host="0.0.0.0", port=port, debug=True)