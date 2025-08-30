import dash
from dash import dcc, html, dash_table, Input, Output, callback
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
import glob
import os

# Load and clean data
def load_clean_data():
    excel_files = glob.glob("squeeze_data_*.xlsx")
    latest_file = max(excel_files, key=os.path.getctime)
    df = pd.read_excel(latest_file)
    
    # Simple, aggressive cleaning
    df = df.dropna(subset=['TICKER'])
    df = df.fillna('Unknown')  # Fill all NaN with 'Unknown'
    
    # Convert numeric columns back to numbers where needed
    numeric_cols = ['P', 'P_NN', 'V', 'G', 'D', 'IV', 'CLOSE', 'VOLUME', 'OPEN', 'HIGH', 'LOW']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    print(f"Loaded {len(df)} clean records")
    return df

df = load_clean_data()

# Initialize app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Enhanced layout
app.layout = dbc.Container([
    html.H1("SqueezeMetrics Financial Dashboard", className="text-center mb-4"),
    
    # Filters
    dbc.Row([
        dbc.Col([
            html.Label("Sector Filter:"),
            dcc.Dropdown(
                id="sector-filter",
                options=[{"label": "All", "value": "All"}] + 
                        [{"label": sector, "value": sector} for sector in sorted(df['SECTOR'].unique()) if sector != 'Unknown'],
                value="All",
                clearable=False
            )
        ], width=4),
        dbc.Col([
            html.Label("Show records:"),
            dcc.Dropdown(
                id="records-filter", 
                options=[
                    {"label": "50", "value": 50},
                    {"label": "100", "value": 100},
                    {"label": "All", "value": len(df)}
                ],
                value=50,
                clearable=False
            )
        ], width=4)
    ], className="mb-4"),
    
    # Metrics cards
    html.Div(id="metrics-cards"),
    
    # Tabs
    dcc.Tabs(id="tabs", value="data", children=[
        dcc.Tab(label="Data Table", value="data"),
        dcc.Tab(label="Charts", value="charts")
    ]),
    
    html.Div(id="tab-content")
])

# Callback for metrics cards
@app.callback(
    Output("metrics-cards", "children"),
    [Input("sector-filter", "value"),
     Input("records-filter", "value")]
)
def update_metrics(sector, records):
    # Filter data
    filtered_df = df.copy()
    if sector != "All":
        filtered_df = filtered_df[filtered_df['SECTOR'] == sector]
    filtered_df = filtered_df.head(records)
    
    return dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"{len(filtered_df)}", className="text-primary"),
                    html.P("Securities")
                ])
            ])
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"{filtered_df['P'].mean():.3f}", className="text-info"),
                    html.P("Avg P Score")
                ])
            ])
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"{filtered_df['P_NN'].mean():.4f}", className="text-success"),
                    html.P("Avg P_NN")
                ])
            ])
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"{len(filtered_df[filtered_df['P_NN'] > 0])}", className="text-warning"),
                    html.P("Positive P_NN")
                ])
            ])
        ], width=3)
    ], className="mb-4")

# Callback for tab content
@app.callback(
    Output("tab-content", "children"),
    [Input("tabs", "value"),
     Input("sector-filter", "value"),
     Input("records-filter", "value")]
)
def update_tab_content(tab, sector, records):
    # Filter data
    filtered_df = df.copy()
    if sector != "All":
        filtered_df = filtered_df[filtered_df['SECTOR'] == sector]
    filtered_df = filtered_df.head(records)
    
    if tab == "data":
        return html.Div([
            html.H3("Data Table", className="mt-3"),
            dash_table.DataTable(
                data=filtered_df.to_dict('records'),
                columns=[
                    {'name': 'Ticker', 'id': 'TICKER'},
                    {'name': 'Name', 'id': 'NAME'},
                    {'name': 'Sector', 'id': 'SECTOR'},
                    {'name': 'P Score', 'id': 'P', 'type': 'numeric', 'format': {'specifier': '.3f'}},
                    {'name': 'P_NN', 'id': 'P_NN', 'type': 'numeric', 'format': {'specifier': '.4f'}},
                    {'name': 'V Score', 'id': 'V', 'type': 'numeric', 'format': {'specifier': '.3f'}},
                    {'name': 'Close', 'id': 'CLOSE', 'type': 'numeric', 'format': {'specifier': '$.2f'}},
                    {'name': 'Volume', 'id': 'VOLUME', 'type': 'numeric', 'format': {'specifier': ',.0f'}},
                ],
                sort_action="native",
                filter_action="native",
                page_size=20,
                style_cell={'textAlign': 'left'},
                style_data_conditional=[
                    {
                        'if': {'filter_query': '{P_NN} > 0'},
                        'backgroundColor': '#d4edda',
                    },
                    {
                        'if': {'filter_query': '{P_NN} < 0'},
                        'backgroundColor': '#f8d7da',
                    }
                ]
            )
        ])
    
    elif tab == "charts":
        # Simple scatter plot
        fig = px.scatter(
            filtered_df,
            x='P', y='P_NN',
            color='SECTOR',
            hover_data=['TICKER', 'NAME'],
            title="P Score vs P_NN (Neural Network Prediction)"
        )
        
        return html.Div([
            html.H3("Analysis Charts", className="mt-3"),
            dcc.Graph(figure=fig)
        ])

if __name__ == '__main__':
    app.run(debug=True, port=8054)