import os
import dash
from dash import dcc, html, dash_table, Input, Output, callback
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
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
    Fetches latest data from SqueezeMetrics API for production deployment
    """
    api_url = "https://squeezemetrics.com/monitor/api/latest?format=csv&key=0B7661B124724CA4C43BED7742F01266945A7B04BF698A758C9101727FE7392D"
    
    try:
        response = requests.get(api_url, timeout=30)
        response.raise_for_status()
        
        # Read CSV data into pandas DataFrame
        df = pd.read_csv(StringIO(response.text))
        
        # Clean data same as local version
        df = df.dropna(subset=['TICKER'])
        df = df.fillna('Unknown')
        
        # Convert numeric columns
        numeric_cols = ['P', 'P_NN', 'V', 'G', 'D', 'IV', 'CLOSE', 'VOLUME', 'OPEN', 'HIGH', 'LOW', 'P_NORM', 'V_NORM', 'G_NORM', 'D_NORM', 'IV_NORM']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        print(f"Loaded {len(df)} clean records from API")
        return df
        
    except Exception as e:
        print(f"Error loading data from API: {e}")
        # Return empty DataFrame with required columns if API fails
        return pd.DataFrame(columns=['TICKER', 'NAME', 'SECTOR', 'INDUSTRY', 'P_NN', 'CLOSE', 'VOLUME'])

# Load data
df = load_data_from_api()

# Enhanced layout with professional styling
app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H1("SqueezeMetrics Financial Dashboard", className="text-center text-white mb-2"),
                html.P(f"Analyzing {len(df)} securities with P_NN neural network predictions", className="text-center text-white-50"),
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
                                        [{"label": sector, "value": sector} for sector in sorted(df['SECTOR'].unique()) if sector != 'Unknown'] if len(df) > 0 else [],
                                value="All",
                                clearable=False
                            )
                        ], width=3),
                        dbc.Col([
                            html.Label("Industry Filter:", className="fw-bold"),
                            dcc.Dropdown(
                                id="industry-filter",
                                options=[{"label": "All Industries", "value": "All"}] + 
                                        [{"label": industry, "value": industry} for industry in sorted(df['INDUSTRY'].unique()) if industry != 'Unknown'] if len(df) > 0 else [],
                                value="All",
                                clearable=False
                            )
                        ], width=3),
                        dbc.Col([
                            html.Label("Records to Show:", className="fw-bold"),
                            dcc.Dropdown(
                                id="records-filter", 
                                options=[
                                    {"label": "Top 50", "value": 50},
                                    {"label": "Top 100", "value": 100},
                                    {"label": "Top 200", "value": 200},
                                    {"label": "All Records", "value": len(df) if len(df) > 0 else 100}
                                ],
                                value=len(df) if len(df) > 0 else 100,
                                clearable=False
                            )
                        ], width=3),
                        dbc.Col([
                            html.Label("Min P_NN Value:", className="fw-bold"),
                            dcc.Input(
                                id="pnn-filter",
                                type="number",
                                value=0,
                                step=0.01,
                                placeholder="Filter by P_NN..."
                            )
                        ], width=3)
                    ]),
                    dbc.Row([
                        dbc.Col([
                            html.Label("ETF Filter:", className="fw-bold mt-3"),
                            dcc.RadioItems(
                                id="etf-filter",
                                options=[
                                    {"label": " Include ETFs", "value": "include"},
                                    {"label": " Exclude ETFs", "value": "exclude"},
                                    {"label": " ETFs Only", "value": "only"}
                                ],
                                value="exclude",
                                inline=True,
                                className="mt-2"
                            )
                        ], width=12)
                    ])
                ])
            ])
        ])
    ], className="mb-4"),
    
    # Metrics Dashboard
    html.Div(id="metrics-cards"),
    
    # Navigation Tabs - Simplified for production
    dcc.Tabs(id="tabs", value="overview", children=[
        dcc.Tab(label="📊 Overview", value="overview"),
        dcc.Tab(label="💼 Portfolio", value="portfolio"),
        dcc.Tab(label="📈 Analysis", value="analysis")
    ]),
    
    html.Div(id="tab-content"),
    
    # Footer
    html.Hr(className="mt-5"),
    html.P("Powered by SqueezeMetrics API | Deployed on Render", className="text-center text-muted")
])

# Basic callbacks for production version
@app.callback(
    Output("metrics-cards", "children"),
    [Input("sector-filter", "value"),
     Input("industry-filter", "value"),
     Input("records-filter", "value"),
     Input("pnn-filter", "value"),
     Input("etf-filter", "value")]
)
def update_metrics(sector, industry, records, min_pnn, etf_filter):
    if len(df) == 0:
        return dbc.Alert("No data available. Please check API connection.", color="warning")
    
    filtered_df = df.copy()
    
    # Apply filters (same logic as full dashboard)
    if etf_filter == "exclude":
        filtered_df = filtered_df[filtered_df['INDUSTRY'] != 'ETF']
    elif etf_filter == "only":
        filtered_df = filtered_df[filtered_df['INDUSTRY'] == 'ETF']
    
    if sector != "All" and sector in filtered_df['SECTOR'].values:
        filtered_df = filtered_df[filtered_df['SECTOR'] == sector]
    
    if industry != "All" and industry in filtered_df['INDUSTRY'].values:
        filtered_df = filtered_df[filtered_df['INDUSTRY'] == industry]
    
    if min_pnn:
        filtered_df = filtered_df[filtered_df['P_NN'] >= min_pnn]
    
    filtered_df = filtered_df.head(records)
    
    return dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"{len(filtered_df)}", className="text-primary mb-0"),
                    html.P("Securities", className="text-muted mb-0")
                ], className="text-center")
            ])
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"{filtered_df['P_NN'].mean():.4f}" if len(filtered_df) > 0 else "0.0000", className="text-success mb-0"),
                    html.P("Avg P_NN", className="text-muted mb-0")
                ], className="text-center")
            ])
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"{len(filtered_df[filtered_df['P_NN'] > 0])}" if len(filtered_df) > 0 else "0", className="text-warning mb-0"),
                    html.P("Positive P_NN", className="text-muted mb-0")
                ], className="text-center")
            ])
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"{filtered_df['VOLUME'].sum():,.0f}" if len(filtered_df) > 0 else "0", className="text-info mb-0"),
                    html.P("Total Volume", className="text-muted mb-0")
                ], className="text-center")
            ])
        ], width=3)
    ], className="mb-4")

@app.callback(
    Output("tab-content", "children"),
    [Input("tabs", "value"),
     Input("sector-filter", "value"),
     Input("industry-filter", "value"),
     Input("records-filter", "value"),
     Input("pnn-filter", "value"),
     Input("etf-filter", "value")]
)
def update_tab_content(tab, sector, industry, records, min_pnn, etf_filter):
    if len(df) == 0:
        return dbc.Alert("No data available from API. Please try refreshing the page.", color="danger")
    
    # Apply same filtering logic
    filtered_df = df.copy()
    
    if etf_filter == "exclude":
        filtered_df = filtered_df[filtered_df['INDUSTRY'] != 'ETF']
    elif etf_filter == "only":
        filtered_df = filtered_df[filtered_df['INDUSTRY'] == 'ETF']
    
    if sector != "All" and sector in filtered_df['SECTOR'].values:
        filtered_df = filtered_df[filtered_df['SECTOR'] == sector]
    
    if industry != "All" and industry in filtered_df['INDUSTRY'].values:
        filtered_df = filtered_df[filtered_df['INDUSTRY'] == industry]
    
    if min_pnn:
        filtered_df = filtered_df[filtered_df['P_NN'] >= min_pnn]
    
    filtered_df = filtered_df.head(records)
    
    if tab == "overview":
        return html.Div([
            html.H3("📊 Data Overview", className="mt-3 mb-3"),
            dash_table.DataTable(
                data=filtered_df.to_dict('records'),
                columns=[
                    {'name': 'Ticker', 'id': 'TICKER'},
                    {'name': 'Name', 'id': 'NAME'},
                    {'name': 'Sector', 'id': 'SECTOR'},
                    {'name': 'P_NN Signal', 'id': 'P_NN', 'type': 'numeric', 'format': {'specifier': '.4f'}},
                    {'name': 'Close', 'id': 'CLOSE', 'type': 'numeric', 'format': {'specifier': '$.2f'}},
                    {'name': 'Volume', 'id': 'VOLUME', 'type': 'numeric', 'format': {'specifier': ',.0f'}}
                ],
                sort_action="native",
                filter_action="native",
                page_size=20,
                style_cell={'textAlign': 'left'},
                style_data_conditional=[
                    {
                        'if': {'filter_query': '{P_NN} > 0'},
                        'backgroundColor': '#d4edda'
                    },
                    {
                        'if': {'filter_query': '{P_NN} < 0'},
                        'backgroundColor': '#f8d7da'
                    }
                ]
            )
        ])
    
    elif tab == "portfolio":
        # Simplified portfolio logic for production
        portfolio_universe = filtered_df[
            (filtered_df['VOLUME'] >= 10_000_000) & 
            (filtered_df['INDUSTRY'] != 'ETF')
        ].copy()
        
        if len(portfolio_universe) < 60:
            return dbc.Alert(f"Insufficient liquid securities ({len(portfolio_universe)} found). Need at least 60 for portfolio construction.", color="warning")
        
        portfolio_universe_sorted = portfolio_universe.sort_values('P_NN', ascending=False)
        long_candidates = portfolio_universe_sorted.head(20)
        short_candidates = portfolio_universe_sorted.tail(40)
        
        return html.Div([
            html.H3("💼 Portfolio Builder", className="mt-3 mb-3"),
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Long Positions (20)"),
                        dbc.CardBody([
                            dash_table.DataTable(
                                data=long_candidates[['TICKER', 'NAME', 'SECTOR', 'P_NN', 'CLOSE', 'VOLUME']].to_dict('records'),
                                columns=[
                                    {'name': 'Ticker', 'id': 'TICKER'},
                                    {'name': 'P_NN', 'id': 'P_NN', 'type': 'numeric', 'format': {'specifier': '.4f'}},
                                    {'name': 'Close', 'id': 'CLOSE', 'type': 'numeric', 'format': {'specifier': '$.2f'}}
                                ],
                                page_size=10,
                                style_data={'backgroundColor': '#d4edda'}
                            )
                        ])
                    ])
                ], width=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Short Positions (40)"),
                        dbc.CardBody([
                            dash_table.DataTable(
                                data=short_candidates[['TICKER', 'NAME', 'SECTOR', 'P_NN', 'CLOSE', 'VOLUME']].to_dict('records'),
                                columns=[
                                    {'name': 'Ticker', 'id': 'TICKER'},
                                    {'name': 'P_NN', 'id': 'P_NN', 'type': 'numeric', 'format': {'specifier': '.4f'}},
                                    {'name': 'Close', 'id': 'CLOSE', 'type': 'numeric', 'format': {'specifier': '$.2f'}}
                                ],
                                page_size=10,
                                style_data={'backgroundColor': '#f8d7da'}
                            )
                        ])
                    ])
                ], width=6)
            ])
        ])
    
    elif tab == "analysis":
        if len(filtered_df) > 0:
            fig = px.scatter(
                filtered_df, 
                x='P_NN', 
                y='CLOSE',
                color='SECTOR',
                hover_data=['TICKER'],
                title="P_NN vs Price Analysis"
            )
            return dcc.Graph(figure=fig)
        else:
            return dbc.Alert("No data for analysis", color="warning")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))  # Render uses PORT env variable
    app.run(host='0.0.0.0', port=port, debug=False)