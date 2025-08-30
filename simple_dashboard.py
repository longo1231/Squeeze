import dash
from dash import dcc, html, dash_table, Input, Output, callback
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
import glob
import os

# Initialize simple app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Load data with proper cleaning
def load_data():
    excel_files = glob.glob("squeeze_data_*.xlsx")
    if excel_files:
        latest_file = max(excel_files, key=os.path.getctime)
        df = pd.read_excel(latest_file)
        
        # Clean all NaN values thoroughly
        df = df.dropna(subset=['TICKER', 'NAME'])  # Drop rows missing essential data
        df = df.fillna({
            'SECTOR': 'Unknown',
            'INDUSTRY': 'Unknown', 
            'P': 0,
            'P_NN': 0,
            'V': 0,
            'G': 0,
            'D': 0,
            'IV': 0,
            'CLOSE': 0,
            'VOLUME': 0
        })
        
        # Ensure all data types are correct
        df['SECTOR'] = df['SECTOR'].astype(str)
        df['INDUSTRY'] = df['INDUSTRY'].astype(str)
        
        print(f"Loaded {len(df)} clean records")
        return df
    return pd.DataFrame()

df = load_data()

# Simple layout
app.layout = dbc.Container([
    html.H1("SqueezeMetrics Dashboard - Simple Version", className="text-center mb-4"),
    
    # Basic data table
    html.Div([
        html.H3("Data Table"),
        dash_table.DataTable(
            id="data-table",
            data=df.head(100).to_dict('records'),  # Show only first 100 rows
            columns=[
                {"name": "Ticker", "id": "TICKER"},
                {"name": "Name", "id": "NAME"}, 
                {"name": "Sector", "id": "SECTOR"},
                {"name": "P", "id": "P", "type": "numeric", "format": {"specifier": ".3f"}},
                {"name": "P_NN", "id": "P_NN", "type": "numeric", "format": {"specifier": ".4f"}},
                {"name": "Close", "id": "CLOSE", "type": "numeric", "format": {"specifier": "$.2f"}},
            ],
            page_size=10,
            sort_action="native"
        )
    ]),
    
    # Simple metrics
    html.Div([
        html.H3("Basic Metrics"),
        html.P(f"Total Records: {len(df)}"),
        html.P(f"Average P Score: {df['P'].mean():.3f}"),
        html.P(f"Average P_NN: {df['P_NN'].mean():.4f}"),
    ], className="mt-4")

])

if __name__ == "__main__":
    app.run(debug=True, port=8052)