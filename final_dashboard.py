import dash
from dash import dcc, html, dash_table, Input, Output, callback
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import dash_bootstrap_components as dbc
import glob
import os
from datetime import datetime

# Load and clean data
def load_clean_data():
    excel_files = glob.glob("squeeze_data_*.xlsx")
    latest_file = max(excel_files, key=os.path.getctime)
    df = pd.read_excel(latest_file)
    
    # Simple, aggressive cleaning
    df = df.dropna(subset=['TICKER'])
    df = df.fillna('Unknown')  # Fill all NaN with 'Unknown'
    
    # Convert numeric columns back to numbers where needed
    numeric_cols = ['P', 'P_NN', 'V', 'G', 'D', 'IV', 'CLOSE', 'VOLUME', 'OPEN', 'HIGH', 'LOW', 'P_NORM', 'V_NORM', 'G_NORM', 'D_NORM', 'IV_NORM']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    print(f"Loaded {len(df)} clean records")
    return df

df = load_clean_data()

# Initialize app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "SqueezeMetrics Financial Dashboard"

# Enhanced layout with professional styling
app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H1("SqueezeMetrics Financial Dashboard", className="text-center text-white mb-2"),
                html.P(f"Analyzing {len(df)} securities with P_NN neural network predictions", className="text-center text-white-50")
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
                                        [{"label": sector, "value": sector} for sector in sorted(df['SECTOR'].unique()) if sector != 'Unknown'],
                                value="All",
                                clearable=False
                            )
                        ], width=3),
                        dbc.Col([
                            html.Label("Industry Filter:", className="fw-bold"),
                            dcc.Dropdown(
                                id="industry-filter",
                                options=[{"label": "All Industries", "value": "All"}] + 
                                        [{"label": industry, "value": industry} for industry in sorted(df['INDUSTRY'].unique()) if industry != 'Unknown'],
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
                                    {"label": "All Records", "value": len(df)}
                                ],
                                value=len(df),
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
    
    # Navigation Tabs
    dcc.Tabs(id="tabs", value="overview", children=[
        dcc.Tab(label="📊 Overview", value="overview"),
        dcc.Tab(label="🏆 Rankings", value="rankings"),
        dcc.Tab(label="🔄 Pair Trades", value="pairs"),
        dcc.Tab(label="📈 Analysis", value="analysis"), 
        dcc.Tab(label="🏢 Sectors", value="sectors"),
        dcc.Tab(label="💼 Portfolio", value="portfolio"),
        dcc.Tab(label="📋 Data Export", value="export")
    ]),
    
    html.Div(id="tab-content")
])

# Callback for metrics cards
@app.callback(
    Output("metrics-cards", "children"),
    [Input("sector-filter", "value"),
     Input("industry-filter", "value"),
     Input("records-filter", "value"),
     Input("pnn-filter", "value"),
     Input("etf-filter", "value")]
)
def update_metrics(sector, industry, records, min_pnn, etf_filter):
    # Filter data
    filtered_df = df.copy()
    
    # ETF filtering
    if etf_filter == "exclude":
        filtered_df = filtered_df[filtered_df['INDUSTRY'] != 'ETF']
    elif etf_filter == "only":
        filtered_df = filtered_df[filtered_df['INDUSTRY'] == 'ETF']
    # "include" means no ETF filtering
    
    if sector != "All":
        filtered_df = filtered_df[filtered_df['SECTOR'] == sector]
    if industry != "All":
        filtered_df = filtered_df[filtered_df['INDUSTRY'] == industry]
    if min_pnn:
        filtered_df = filtered_df[filtered_df['P_NN'] >= min_pnn]
    filtered_df = filtered_df.head(records)
    
    if len(filtered_df) == 0:
        return dbc.Alert("No data matches the current filters.", color="warning")
    
    return dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.I(className="fas fa-list-alt fa-2x text-primary mb-2"),
                    html.H4(f"{len(filtered_df):,}", className="text-primary mb-0"),
                    html.P("Securities", className="text-muted mb-0")
                ], className="text-center")
            ], className="shadow-sm")
        ], width=2),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.I(className="fas fa-brain fa-2x text-success mb-2"),
                    html.H4(f"{filtered_df['P_NN'].mean():.4f}", className="text-success mb-0"),
                    html.P("Avg P_NN", className="text-muted mb-0")
                ], className="text-center")
            ], className="shadow-sm")
        ], width=2),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.I(className="fas fa-chart-line fa-2x text-info mb-2"),
                    html.H4(f"{len(filtered_df[filtered_df['P_NN'] > 0]):,}", className="text-info mb-0"),
                    html.P("Positive P_NN", className="text-muted mb-0")
                ], className="text-center")
            ], className="shadow-sm")
        ], width=2),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.I(className="fas fa-percentage fa-2x text-warning mb-2"),
                    html.H4(f"{(len(filtered_df[filtered_df['P_NN'] > 0]) / max(len(filtered_df), 1) * 100):.1f}%", className="text-warning mb-0"),
                    html.P("Success Rate", className="text-muted mb-0")
                ], className="text-center")
            ], className="shadow-sm")
        ], width=2),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.I(className="fas fa-arrow-up fa-2x text-danger mb-2"),
                    html.H4(f"{filtered_df['P_NN'].max():.4f}", className="text-danger mb-0"),
                    html.P("Max P_NN", className="text-muted mb-0")
                ], className="text-center")
            ], className="shadow-sm")
        ], width=2),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.I(className="fas fa-dollar-sign fa-2x text-secondary mb-2"),
                    html.H4(f"{filtered_df['VOLUME'].sum():,.0f}", className="text-secondary mb-0"),
                    html.P("Total Volume", className="text-muted mb-0")
                ], className="text-center")
            ], className="shadow-sm")
        ], width=2)
    ], className="mb-4")

# Callback for tab content
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
    # Filter data
    filtered_df = df.copy()
    
    # ETF filtering
    if etf_filter == "exclude":
        filtered_df = filtered_df[filtered_df['INDUSTRY'] != 'ETF']
    elif etf_filter == "only":
        filtered_df = filtered_df[filtered_df['INDUSTRY'] == 'ETF']
    # "include" means no ETF filtering
    
    if sector != "All":
        filtered_df = filtered_df[filtered_df['SECTOR'] == sector]
    if industry != "All":
        filtered_df = filtered_df[filtered_df['INDUSTRY'] == industry]
    if min_pnn:
        filtered_df = filtered_df[filtered_df['P_NN'] >= min_pnn]
    filtered_df = filtered_df.head(records)
    
    if len(filtered_df) == 0:
        return dbc.Alert("No data matches the current filters.", color="warning")
    
    if tab == "overview":
        return html.Div([
            html.H3("📊 Securities Overview", className="mt-3 mb-3"),
            dbc.Alert([
                html.Strong("💡 Filtering Tips: "),
                "Type in column filters below. Case-insensitive partial matching! Try: 'tech' (finds Technology), 'apple' (finds Apple Inc), '>0.1' (P_NN > 0.1)"
            ], color="info", className="mb-3"),
            dash_table.DataTable(
                data=filtered_df.to_dict('records'),
                columns=[
                    {'name': 'Ticker', 'id': 'TICKER'},
                    {'name': 'Name', 'id': 'NAME'}, 
                    {'name': 'Sector', 'id': 'SECTOR'},
                    {'name': 'P Score', 'id': 'P', 'type': 'numeric', 'format': {'specifier': '.3f'}},
                    {'name': 'P_NN 🧠', 'id': 'P_NN', 'type': 'numeric', 'format': {'specifier': '.4f'}},
                    {'name': 'V Score', 'id': 'V', 'type': 'numeric', 'format': {'specifier': '.3f'}},
                    {'name': 'G Score', 'id': 'G', 'type': 'numeric', 'format': {'specifier': '.3f'}},
                    {'name': 'D Score', 'id': 'D', 'type': 'numeric', 'format': {'specifier': '.3f'}},
                    {'name': 'IV', 'id': 'IV', 'type': 'numeric', 'format': {'specifier': '.1f'}},
                    {'name': 'Close ($)', 'id': 'CLOSE', 'type': 'numeric', 'format': {'specifier': '$.2f'}},
                    {'name': 'Volume', 'id': 'VOLUME', 'type': 'numeric', 'format': {'specifier': ',.0f'}},
                ],
                sort_action="native",
                filter_action="native",
                filter_options={"case": "insensitive"},
                page_action="native",
                page_size=50,
                style_cell={'textAlign': 'left', 'fontSize': 12},
                style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'},
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
                    },
                    {
                        'if': {'filter_query': '{P_NN} > 0 && {P_NN} <= 0.1'},
                        'backgroundColor': '#fff3cd',
                        'color': 'black',
                    }
                ]
            )
        ])
    
    elif tab == "rankings":
        # Create sector leaderboards and industry analysis
        
        # Get sector leaderboards (top 10 and bottom 10 per sector)
        sectors = [s for s in filtered_df['SECTOR'].unique() if s not in ['Unknown', '-']]
        
        # Industry P_NN dispersion analysis
        industry_stats = filtered_df.groupby('INDUSTRY').agg({
            'P_NN': ['mean', 'std', 'min', 'max', 'count']
        }).round(4)
        industry_stats.columns = ['Avg_P_NN', 'StdDev_P_NN', 'Min_P_NN', 'Max_P_NN', 'Count']
        industry_stats['P_NN_Range'] = industry_stats['Max_P_NN'] - industry_stats['Min_P_NN']
        industry_stats = industry_stats.reset_index()
        industry_stats = industry_stats[industry_stats['Count'] >= 3]  # Only industries with 3+ stocks
        industry_stats = industry_stats.sort_values('P_NN_Range', ascending=False)
        
        # Sector momentum analysis
        sector_momentum = filtered_df.groupby('SECTOR').agg({
            'P_NN': ['mean', 'count']
        }).round(4)
        sector_momentum.columns = ['Avg_P_NN', 'Count']
        sector_momentum = sector_momentum.reset_index()
        sector_momentum = sector_momentum[sector_momentum['Count'] >= 5]  # Only sectors with 5+ stocks
        sector_momentum = sector_momentum.sort_values('Avg_P_NN', ascending=False)
        
        # Create sector leaderboard cards
        sector_cards = []
        for i, sector in enumerate(sectors[:6]):  # Show top 6 sectors
            sector_data = filtered_df[filtered_df['SECTOR'] == sector].sort_values('P_NN', ascending=False)
            if len(sector_data) >= 5:  # Only show sectors with enough stocks
                top_5 = sector_data.head(5)
                bottom_5 = sector_data.tail(5)
                
                card = dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(f"{sector} P_NN Leaders & Laggards"),
                        dbc.CardBody([
                            html.H6("🔥 Top 5 (Long Ideas)", className="text-success"),
                            html.Div([
                                html.P(f"{row['TICKER']}: {row['P_NN']:.4f}", 
                                       className="mb-1 small") 
                                for _, row in top_5.iterrows()
                            ]),
                            html.Hr(),
                            html.H6("❄️ Bottom 5 (Short Ideas)", className="text-danger"),
                            html.Div([
                                html.P(f"{row['TICKER']}: {row['P_NN']:.4f}", 
                                       className="mb-1 small") 
                                for _, row in bottom_5.iterrows()
                            ])
                        ])
                    ], className="mb-3")
                ], width=4)
                sector_cards.append(card)
        
        # Create charts
        sector_chart = px.bar(
            sector_momentum, x='SECTOR', y='Avg_P_NN',
            title="Sector P_NN Momentum (Average P_NN by Sector)",
            color='Avg_P_NN', color_continuous_scale='RdYlGn'
        )
        sector_chart.update_xaxis(tickangle=45)
        
        dispersion_chart = px.bar(
            industry_stats.head(15), x='INDUSTRY', y='P_NN_Range',
            title="Top 15 Industries by P_NN Dispersion (Best for Pair Trading)",
            hover_data=['Avg_P_NN', 'Count']
        )
        dispersion_chart.update_xaxis(tickangle=45)
        
        return html.Div([
            html.H3("🏆 P_NN Rankings & Industry Analysis", className="mt-3 mb-3"),
            
            # Sector Leaderboards
            html.H4("📈 Sector Leaders & Laggards", className="mb-3"),
            dbc.Row(sector_cards),
            
            # Charts
            dbc.Row([
                dbc.Col([
                    dcc.Graph(figure=sector_chart)
                ], width=6),
                dbc.Col([
                    dcc.Graph(figure=dispersion_chart)
                ], width=6)
            ]),
            
            # Industry Dispersion Table
            html.H4("🎯 Industry P_NN Dispersion Analysis", className="mt-4 mb-3"),
            html.P("Industries with high P_NN dispersion offer the best pair trading opportunities", 
                   className="text-muted"),
            dash_table.DataTable(
                data=industry_stats.head(20).to_dict('records'),
                columns=[
                    {'name': 'Industry', 'id': 'INDUSTRY'},
                    {'name': 'Avg P_NN', 'id': 'Avg_P_NN', 'type': 'numeric', 'format': {'specifier': '.4f'}},
                    {'name': 'P_NN Range', 'id': 'P_NN_Range', 'type': 'numeric', 'format': {'specifier': '.4f'}},
                    {'name': 'Std Dev', 'id': 'StdDev_P_NN', 'type': 'numeric', 'format': {'specifier': '.4f'}},
                    {'name': 'Min P_NN', 'id': 'Min_P_NN', 'type': 'numeric', 'format': {'specifier': '.4f'}},
                    {'name': 'Max P_NN', 'id': 'Max_P_NN', 'type': 'numeric', 'format': {'specifier': '.4f'}},
                    {'name': 'Stock Count', 'id': 'Count', 'type': 'numeric'}
                ],
                sort_action="native",
                filter_action="native",
                filter_options={"case": "insensitive"},
                style_cell={'textAlign': 'left', 'fontSize': 12},
                style_data_conditional=[
                    {
                        'if': {'filter_query': '{P_NN_Range} > 0.2'},
                        'backgroundColor': '#d4edda',
                        'color': 'black',
                    },
                    {
                        'if': {'filter_query': '{P_NN_Range} > 0.1 && {P_NN_Range} <= 0.2'},
                        'backgroundColor': '#fff3cd',
                        'color': 'black',
                    }
                ]
            ),
            
            # Sector Momentum Table
            html.H4("🚀 Sector Momentum Rankings", className="mt-4 mb-3"),
            dash_table.DataTable(
                data=sector_momentum.to_dict('records'),
                columns=[
                    {'name': 'Sector', 'id': 'SECTOR'},
                    {'name': 'Average P_NN', 'id': 'Avg_P_NN', 'type': 'numeric', 'format': {'specifier': '.4f'}},
                    {'name': 'Stock Count', 'id': 'Count', 'type': 'numeric'}
                ],
                sort_action="native",
                filter_action="native",
                filter_options={"case": "insensitive"},
                style_cell={'textAlign': 'left'},
                style_data_conditional=[
                    {
                        'if': {'filter_query': '{Avg_P_NN} > 0.05'},
                        'backgroundColor': '#d4edda',
                        'color': 'black',
                    },
                    {
                        'if': {'filter_query': '{Avg_P_NN} < -0.05'},
                        'backgroundColor': '#f8d7da',
                        'color': 'black',
                    }
                ]
            )
        ])
    
    elif tab == "pairs":
        # Pair Trade Generator
        
        # Add dollar volume for market cap proxy
        filtered_df_copy = filtered_df.copy()
        filtered_df_copy['DOLLAR_VOLUME'] = filtered_df_copy['CLOSE'] * filtered_df_copy['VOLUME']
        
        # Create market cap buckets
        q25, q75 = filtered_df_copy['DOLLAR_VOLUME'].quantile([0.25, 0.75])
        filtered_df_copy['MARKET_CAP_BUCKET'] = pd.cut(
            filtered_df_copy['DOLLAR_VOLUME'],
            bins=[0, q25, q75, float('inf')],
            labels=['Small', 'Mid', 'Large']
        )
        
        # Generate pairs within same industry
        industries_with_pairs = []
        all_pairs = []
        
        for industry in filtered_df_copy['INDUSTRY'].unique():
            if industry in ['Unknown', 'ETF']:
                continue
                
            industry_stocks = filtered_df_copy[filtered_df_copy['INDUSTRY'] == industry]
            if len(industry_stocks) < 2:
                continue
            
            # Sort by P_NN
            industry_stocks = industry_stocks.sort_values('P_NN', ascending=False)
            
            # Find pairs with sufficient P_NN spread
            high_pnn = industry_stocks[industry_stocks['P_NN'] > 0.02]  # Longs
            low_pnn = industry_stocks[industry_stocks['P_NN'] < -0.02]   # Shorts
            
            if len(high_pnn) == 0 or len(low_pnn) == 0:
                continue
            
            # Generate pairs within same market cap bucket when possible
            for _, long_stock in high_pnn.head(3).iterrows():  # Top 3 longs
                for _, short_stock in low_pnn.tail(3).iterrows():  # Bottom 3 shorts
                    
                    pnn_spread = long_stock['P_NN'] - short_stock['P_NN']
                    
                    # Only include pairs with meaningful spread
                    if pnn_spread < 0.05:
                        continue
                    
                    # Market cap compatibility check
                    same_bucket = long_stock['MARKET_CAP_BUCKET'] == short_stock['MARKET_CAP_BUCKET']
                    
                    # Volume check for liquidity
                    min_volume = min(long_stock['VOLUME'], short_stock['VOLUME'])
                    if min_volume < 100000:  # Skip illiquid stocks
                        continue
                    
                    pair = {
                        'INDUSTRY': industry,
                        'LONG_TICKER': long_stock['TICKER'],
                        'LONG_P_NN': long_stock['P_NN'],
                        'LONG_CLOSE': long_stock['CLOSE'],
                        'LONG_VOLUME': long_stock['VOLUME'],
                        'LONG_MARKET_CAP': long_stock['MARKET_CAP_BUCKET'],
                        'SHORT_TICKER': short_stock['TICKER'],
                        'SHORT_P_NN': short_stock['P_NN'],
                        'SHORT_CLOSE': short_stock['CLOSE'],
                        'SHORT_VOLUME': short_stock['VOLUME'],
                        'SHORT_MARKET_CAP': short_stock['MARKET_CAP_BUCKET'],
                        'P_NN_SPREAD': pnn_spread,
                        'MIN_VOLUME': min_volume,
                        'MARKET_CAP_MATCH': same_bucket
                    }
                    all_pairs.append(pair)
            
            if len(high_pnn) > 0 and len(low_pnn) > 0:
                industries_with_pairs.append({
                    'INDUSTRY': industry,
                    'LONG_COUNT': len(high_pnn),
                    'SHORT_COUNT': len(low_pnn),
                    'TOTAL_STOCKS': len(industry_stocks),
                    'AVG_P_NN_SPREAD': industry_stocks['P_NN'].max() - industry_stocks['P_NN'].min()
                })
        
        # Convert to DataFrames
        pairs_df = pd.DataFrame(all_pairs)
        industries_df = pd.DataFrame(industries_with_pairs)
        
        if len(pairs_df) == 0:
            return html.Div([
                html.H3("🔄 Pair Trade Generator", className="mt-3 mb-3"),
                dbc.Alert("No suitable pairs found with current filters. Try adjusting P_NN or sector filters.", 
                         color="warning")
            ])
        
        # Sort pairs by P_NN spread (best opportunities first)
        pairs_df = pairs_df.sort_values('P_NN_SPREAD', ascending=False)
        industries_df = industries_df.sort_values('AVG_P_NN_SPREAD', ascending=False)
        
        # Show all pairs with pagination
        display_pairs = pairs_df  # Show all pairs
        
        return html.Div([
            html.H3("🔄 Pair Trade Generator", className="mt-3 mb-3"),
            html.P("Auto-generated long/short pairs within same industries based on P_NN spreads", 
                   className="text-muted"),
            
            
            # Summary cards
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4(f"{len(pairs_df):,}", className="text-primary"),
                            html.P("Total Pairs Generated", className="mb-0")
                        ])
                    ])
                ], width=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4(f"{len(industries_df):,}", className="text-success"),
                            html.P("Industries with Pairs", className="mb-0")
                        ])
                    ])
                ], width=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4(f"{pairs_df['P_NN_SPREAD'].max():.4f}", className="text-warning"),
                            html.P("Max P_NN Spread", className="mb-0")
                        ])
                    ])
                ], width=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4(f"{len(pairs_df[pairs_df['MARKET_CAP_MATCH']])}", className="text-info"),
                            html.P("Market Cap Matched", className="mb-0")
                        ])
                    ])
                ], width=3)
            ], className="mb-4"),
            
            # All pair trades table with pagination  
            html.H4(f"🔥 All {len(pairs_df)} Pair Trade Opportunities", className="mb-3"),
            dbc.Alert([
                html.Strong("🎯 Filter Examples: "),
                "Industry: 'software', 'bio' | Long/Short: 'AAPL', 'tesla' | P_NN Spread: '>0.15' | Cap Match: 'true'"
            ], color="info", className="mb-3"),
            dash_table.DataTable(
                data=display_pairs.to_dict('records'),
                columns=[
                    {'name': 'Industry', 'id': 'INDUSTRY'},
                    {'name': 'Long', 'id': 'LONG_TICKER'},
                    {'name': 'Long P_NN', 'id': 'LONG_P_NN', 'type': 'numeric', 'format': {'specifier': '.4f'}},
                    {'name': 'Short', 'id': 'SHORT_TICKER'},
                    {'name': 'Short P_NN', 'id': 'SHORT_P_NN', 'type': 'numeric', 'format': {'specifier': '.4f'}},
                    {'name': 'P_NN Spread', 'id': 'P_NN_SPREAD', 'type': 'numeric', 'format': {'specifier': '.4f'}},
                    {'name': 'Long Price', 'id': 'LONG_CLOSE', 'type': 'numeric', 'format': {'specifier': '$.2f'}},
                    {'name': 'Short Price', 'id': 'SHORT_CLOSE', 'type': 'numeric', 'format': {'specifier': '$.2f'}},
                    {'name': 'Min Volume', 'id': 'MIN_VOLUME', 'type': 'numeric', 'format': {'specifier': ',.0f'}},
                    {'name': 'Cap Match', 'id': 'MARKET_CAP_MATCH', 'type': 'text'}
                ],
                sort_action="native",
                filter_action="native",
                filter_options={"case": "insensitive"},
                page_action="native",
                page_size=25,
                style_cell={'textAlign': 'left', 'fontSize': 11},
                style_data_conditional=[
                    {
                        'if': {'filter_query': '{P_NN_SPREAD} > 0.15'},
                        'backgroundColor': '#d4edda',
                        'color': 'black',
                    },
                    {
                        'if': {'filter_query': '{P_NN_SPREAD} > 0.10 && {P_NN_SPREAD} <= 0.15'},
                        'backgroundColor': '#fff3cd',
                        'color': 'black',
                    },
                    {
                        'if': {'filter_query': '{MARKET_CAP_MATCH} = True'},
                        'fontWeight': 'bold'
                    }
                ]
            ),
            
            # Industry pair opportunities
            html.H4("🎯 Industries with Best Pair Opportunities", className="mt-4 mb-3"),
            dash_table.DataTable(
                data=industries_df.head(15).to_dict('records'),
                columns=[
                    {'name': 'Industry', 'id': 'INDUSTRY'},
                    {'name': 'Long Ideas', 'id': 'LONG_COUNT', 'type': 'numeric'},
                    {'name': 'Short Ideas', 'id': 'SHORT_COUNT', 'type': 'numeric'},
                    {'name': 'Total Stocks', 'id': 'TOTAL_STOCKS', 'type': 'numeric'},
                    {'name': 'P_NN Spread', 'id': 'AVG_P_NN_SPREAD', 'type': 'numeric', 'format': {'specifier': '.4f'}}
                ],
                sort_action="native",
                filter_action="native",
                filter_options={"case": "insensitive"},
                style_cell={'textAlign': 'left'},
                style_data_conditional=[
                    {
                        'if': {'filter_query': '{AVG_P_NN_SPREAD} > 0.3'},
                        'backgroundColor': '#d4edda',
                        'color': 'black',
                    }
                ]
            ),
            
            # Trading notes
            dbc.Card([
                dbc.CardHeader("📝 Trading Notes"),
                dbc.CardBody([
                    html.P("🎯 P_NN Spread Interpretation:", className="fw-bold"),
                    html.Ul([
                        html.Li("Green (>0.15): Exceptional pair opportunity"),
                        html.Li("Yellow (0.10-0.15): Strong pair opportunity"), 
                        html.Li("White (<0.10): Moderate pair opportunity")
                    ]),
                    html.P("💡 Market Cap Match (Bold): Same size bucket for cleaner pair", className="fw-bold mt-3"),
                    html.P("⚡ Min Volume: Liquidity check for execution", className="fw-bold"),
                ])
            ], className="mt-4")
        ])
    
    elif tab == "analysis":
        # Multiple charts
        fig1 = px.scatter(
            filtered_df, x='P', y='P_NN', color='SECTOR', size='VOLUME',
            hover_data=['TICKER', 'NAME'], title="P Score vs P_NN - Neural Network Analysis"
        )
        
        fig2 = px.scatter(
            filtered_df, x='V', y='G', color='SECTOR', size='VOLUME', 
            hover_data=['TICKER', 'NAME', 'P_NN'], title="V Score vs G Score Analysis"
        )
        
        fig3 = px.histogram(
            filtered_df, x='P_NN', nbins=30, title="P_NN Distribution"
        )
        
        return html.Div([
            html.H3("📈 Advanced Analysis", className="mt-3 mb-3"),
            dbc.Row([
                dbc.Col([dcc.Graph(figure=fig1)], width=6),
                dbc.Col([dcc.Graph(figure=fig2)], width=6)
            ]),
            dbc.Row([
                dbc.Col([dcc.Graph(figure=fig3)], width=12)
            ])
        ])
    
    elif tab == "sectors":
        # Sector analysis
        sector_summary = filtered_df.groupby('SECTOR').agg({
            'P': 'mean', 'P_NN': 'mean', 'V': 'mean', 'G': 'mean', 'D': 'mean',
            'VOLUME': 'sum', 'TICKER': 'count'
        }).round(4)
        sector_summary.columns = ['Avg_P', 'Avg_P_NN', 'Avg_V', 'Avg_G', 'Avg_D', 'Total_Volume', 'Count']
        sector_summary = sector_summary.reset_index()
        
        fig = go.Figure(data=go.Heatmap(
            z=[sector_summary['Avg_P'], sector_summary['Avg_P_NN'], sector_summary['Avg_V']],
            x=sector_summary['SECTOR'],
            y=['P Score', 'P_NN (Neural Net)', 'V Score'],
            colorscale='RdYlGn'
        ))
        fig.update_layout(title="Sector Performance Heatmap")
        
        return html.Div([
            html.H3("🏢 Sector Comparison", className="mt-3 mb-3"),
            dcc.Graph(figure=fig),
            html.H4("Sector Summary Table", className="mt-4 mb-3"),
            dash_table.DataTable(
                data=sector_summary.to_dict('records'),
                columns=[{'name': col, 'id': col, 'type': 'numeric' if col != 'SECTOR' else 'text'} for col in sector_summary.columns],
                sort_action="native",
                filter_action="native",
                filter_options={"case": "insensitive"},
                style_cell={'textAlign': 'left'}
            )
        ])
    
    elif tab == "portfolio":
        # Portfolio construction with constraints
        
        # Apply $10M volume filter and exclude ETFs
        portfolio_universe = filtered_df[
            (filtered_df['VOLUME'] >= 10_000_000) & 
            (filtered_df['INDUSTRY'] != 'ETF')
        ].copy()
        
        # Sort by P_NN for long/short selection
        portfolio_universe_sorted = portfolio_universe.sort_values('P_NN', ascending=False)
        
        # Select candidates for longs (top P_NN values) and shorts (bottom P_NN values)
        # Take top 50 for longs and bottom 50 for shorts to ensure we have enough candidates
        long_candidates = portfolio_universe_sorted.head(50)
        short_candidates = portfolio_universe_sorted.tail(50)
        
        # Build balanced portfolio with constraints
        def build_balanced_portfolio(candidates, target_count, is_long=True):
            selected = []
            sector_counts = {}
            industry_counts = {}
            
            for _, stock in candidates.iterrows():
                sector = stock['SECTOR']
                industry = stock['INDUSTRY']
                
                # Check constraints
                if sector_counts.get(sector, 0) >= 4:  # Max 4 per sector
                    continue
                if industry_counts.get(industry, 0) >= 2:  # Max 2 per industry
                    continue
                
                # Add to portfolio
                selected.append(stock)
                sector_counts[sector] = sector_counts.get(sector, 0) + 1
                industry_counts[industry] = industry_counts.get(industry, 0) + 1
                
                if len(selected) >= target_count:
                    break
            
            return pd.DataFrame(selected)
        
        # Build 20 longs and 40 shorts
        long_portfolio = build_balanced_portfolio(long_candidates, 20, True)
        short_portfolio = build_balanced_portfolio(short_candidates, 40, False)
        
        # Calculate position sizes (equal dollar weight within buckets)
        portfolio_value = 10_000_000  # $10M portfolio
        long_allocation = 0.5  # 50% long
        short_allocation = 0.5  # 50% short
        
        if len(long_portfolio) > 0:
            long_position_size = (portfolio_value * long_allocation) / len(long_portfolio)
            long_portfolio['POSITION_SIZE'] = long_position_size
            long_portfolio['POSITION_TYPE'] = 'LONG'
        
        if len(short_portfolio) > 0:
            short_position_size = (portfolio_value * short_allocation) / len(short_portfolio)
            short_portfolio['POSITION_SIZE'] = short_position_size
            short_portfolio['POSITION_TYPE'] = 'SHORT'
        
        return html.Div([
            html.H3("💼 Portfolio Builder", className="mt-3 mb-3"),
            
            # Portfolio Summary
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Portfolio Summary"),
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    html.H5(f"{len(portfolio_universe):,}", className="text-primary"),
                                    html.P("Securities in Universe", className="text-muted mb-0"),
                                    html.Small(f"(Volume ≥ $10M, No ETFs)", className="text-muted")
                                ], width=3),
                                dbc.Col([
                                    html.H5(f"{len(long_portfolio)}", className="text-success"),
                                    html.P("Long Positions", className="text-muted mb-0"),
                                    html.Small(f"Top P_NN Signals", className="text-muted")
                                ], width=3),
                                dbc.Col([
                                    html.H5(f"{len(short_portfolio)}", className="text-danger"),
                                    html.P("Short Positions", className="text-muted mb-0"),
                                    html.Small(f"Bottom P_NN Signals", className="text-muted")
                                ], width=3),
                                dbc.Col([
                                    html.H5(f"${portfolio_value/1_000_000:.1f}M", className="text-info"),
                                    html.P("Total Portfolio", className="text-muted mb-0"),
                                    html.Small(f"50% Long / 50% Short", className="text-muted")
                                ], width=3)
                            ])
                        ])
                    ])
                ])
            ], className="mb-4"),
            
            # Portfolio Tabs
            dcc.Tabs(id="portfolio-tabs", value="long", children=[
                dcc.Tab(label=f"📈 Long Positions ({len(long_portfolio)})", value="long"),
                dcc.Tab(label=f"📉 Short Positions ({len(short_portfolio)})", value="short"),
                dcc.Tab(label="⚖️ Balance Analysis", value="balance")
            ]),
            
            html.Div(id="portfolio-tab-content"),
            
            # Add JavaScript for portfolio tab switching
            dcc.Store(id="long-portfolio", data=long_portfolio.to_dict('records') if len(long_portfolio) > 0 else []),
            dcc.Store(id="short-portfolio", data=short_portfolio.to_dict('records') if len(short_portfolio) > 0 else [])
        ])
    
    elif tab == "export":
        return html.Div([
            html.H3("📋 Data Export", className="mt-3 mb-3"),
            dbc.Card([
                dbc.CardBody([
                    html.P(f"Current filter results: {len(filtered_df)} securities"),
                    html.P("Export options:"),
                    dbc.Button("Download CSV", color="primary", className="me-2"),
                    dbc.Button("Download Excel", color="success", className="me-2"),
                    html.Hr(),
                    html.P("Quick Stats:", className="fw-bold"),
                    html.Ul([
                        html.Li(f"Securities with positive P_NN: {len(filtered_df[filtered_df['P_NN'] > 0])}"),
                        html.Li(f"Average P_NN: {filtered_df['P_NN'].mean():.4f}"),
                        html.Li(f"Top sector by count: {filtered_df['SECTOR'].value_counts().index[0]}"),
                        html.Li(f"Total volume: ${filtered_df['VOLUME'].sum():,.0f}")
                    ])
                ])
            ])
        ])

# Callback for portfolio sub-tabs
@app.callback(
    Output("portfolio-tab-content", "children"),
    [Input("portfolio-tabs", "value"),
     Input("long-portfolio", "data"),
     Input("short-portfolio", "data")]
)
def update_portfolio_tabs(portfolio_tab, long_data, short_data):
    if portfolio_tab == "long":
        if not long_data:
            return html.Div([
                dbc.Alert("No long positions found with current criteria (Top P_NN, Volume ≥ $10M)", color="warning")
            ])
        
        long_df = pd.DataFrame(long_data)
        return html.Div([
            html.H4("📈 Long Positions", className="mt-3 mb-3"),
            dash_table.DataTable(
                data=long_df.to_dict('records'),
                columns=[
                    {'name': 'Ticker', 'id': 'TICKER'},
                    {'name': 'Name', 'id': 'NAME'},
                    {'name': 'Sector', 'id': 'SECTOR'},
                    {'name': 'Industry', 'id': 'INDUSTRY'},
                    {'name': 'P_NN Signal', 'id': 'P_NN', 'type': 'numeric', 'format': {'specifier': '.4f'}},
                    {'name': 'Close Price', 'id': 'CLOSE', 'type': 'numeric', 'format': {'specifier': '$.2f'}},
                    {'name': 'Volume', 'id': 'VOLUME', 'type': 'numeric', 'format': {'specifier': ',.0f'}},
                    {'name': 'Position Size', 'id': 'POSITION_SIZE', 'type': 'numeric', 'format': {'specifier': '$,.0f'}}
                ],
                sort_action="native",
                filter_action="native",
                page_size=20,
                style_cell={'textAlign': 'left'},
                style_data_conditional=[
                    {
                        'if': {'column_id': 'P_NN'},
                        'backgroundColor': '#d4edda',
                        'color': 'black'
                    }
                ]
            )
        ])
    
    elif portfolio_tab == "short":
        if not short_data:
            return html.Div([
                dbc.Alert("No short positions found with current criteria (Bottom P_NN, Volume ≥ $10M)", color="warning")
            ])
        
        short_df = pd.DataFrame(short_data)
        return html.Div([
            html.H4("📉 Short Positions", className="mt-3 mb-3"),
            dash_table.DataTable(
                data=short_df.to_dict('records'),
                columns=[
                    {'name': 'Ticker', 'id': 'TICKER'},
                    {'name': 'Name', 'id': 'NAME'},
                    {'name': 'Sector', 'id': 'SECTOR'},
                    {'name': 'Industry', 'id': 'INDUSTRY'},
                    {'name': 'P_NN Signal', 'id': 'P_NN', 'type': 'numeric', 'format': {'specifier': '.4f'}},
                    {'name': 'Close Price', 'id': 'CLOSE', 'type': 'numeric', 'format': {'specifier': '$.2f'}},
                    {'name': 'Volume', 'id': 'VOLUME', 'type': 'numeric', 'format': {'specifier': ',.0f'}},
                    {'name': 'Position Size', 'id': 'POSITION_SIZE', 'type': 'numeric', 'format': {'specifier': '$,.0f'}}
                ],
                sort_action="native",
                filter_action="native",
                page_size=20,
                style_cell={'textAlign': 'left'},
                style_data_conditional=[
                    {
                        'if': {'column_id': 'P_NN'},
                        'backgroundColor': '#f8d7da',
                        'color': 'black'
                    }
                ]
            )
        ])
    
    elif portfolio_tab == "balance":
        # Create balance analysis
        long_df = pd.DataFrame(long_data) if long_data else pd.DataFrame()
        short_df = pd.DataFrame(short_data) if short_data else pd.DataFrame()
        
        # Sector distribution
        long_sectors = long_df['SECTOR'].value_counts() if len(long_df) > 0 else pd.Series()
        short_sectors = short_df['SECTOR'].value_counts() if len(short_df) > 0 else pd.Series()
        
        # Industry distribution  
        long_industries = long_df['INDUSTRY'].value_counts() if len(long_df) > 0 else pd.Series()
        short_industries = short_df['INDUSTRY'].value_counts() if len(short_df) > 0 else pd.Series()
        
        return html.Div([
            html.H4("⚖️ Portfolio Balance Analysis", className="mt-3 mb-3"),
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Sector Distribution"),
                        dbc.CardBody([
                            html.H6("Long Positions:"),
                            html.Ul([html.Li(f"{sector}: {count}") for sector, count in long_sectors.items()]) if len(long_sectors) > 0 else html.P("No long positions"),
                            html.H6("Short Positions:", className="mt-3"),
                            html.Ul([html.Li(f"{sector}: {count}") for sector, count in short_sectors.items()]) if len(short_sectors) > 0 else html.P("No short positions")
                        ])
                    ])
                ], width=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Risk Metrics"),
                        dbc.CardBody([
                            html.P(f"Portfolio Constraints:"),
                            html.Ul([
                                html.Li("Maximum 4 positions per sector"),
                                html.Li("Maximum 2 positions per industry"),
                                html.Li("Minimum $10M daily volume"),
                                html.Li("Equal dollar weighting within buckets")
                            ]),
                            html.Hr(),
                            html.P("Rebalancing Triggers:"),
                            html.Ul([
                                html.Li("Long signals: P_NN drops below 0.03"),
                                html.Li("Short signals: P_NN rises above -0.03"),
                                html.Li("Volume falls below $10M threshold")
                            ])
                        ])
                    ])
                ], width=6)
            ])
        ])

if __name__ == '__main__':
    app.run(debug=True, port=8055)