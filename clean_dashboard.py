import dash
from dash import dcc, html, dash_table
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
    numeric_cols = ['P', 'P_NN', 'V', 'G', 'D', 'IV', 'CLOSE', 'VOLUME']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    print(f"Loaded {len(df)} clean records")
    return df

df = load_clean_data()

# Initialize app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Simple layout with just basics
app.layout = html.Div([
    html.H1("SqueezeMetrics Dashboard", style={'textAlign': 'center'}),
    
    html.Div([
        html.H3("Summary"),
        html.P(f"Total Securities: {len(df)}"),
        html.P(f"Average P Score: {df['P'].mean():.3f}"),
        html.P(f"Average P_NN: {df['P_NN'].mean():.4f}"),
    ], style={'padding': '20px'}),
    
    html.Div([
        html.H3("Data Table"),
        dash_table.DataTable(
            data=df.head(50).to_dict('records'),
            columns=[
                {'name': 'Ticker', 'id': 'TICKER'},
                {'name': 'Name', 'id': 'NAME'},
                {'name': 'Sector', 'id': 'SECTOR'},
                {'name': 'P Score', 'id': 'P'},
                {'name': 'P_NN', 'id': 'P_NN'},
                {'name': 'Close', 'id': 'CLOSE'},
                {'name': 'Volume', 'id': 'VOLUME'},
            ],
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'left'},
            page_size=20
        )
    ], style={'padding': '20px'})
])

if __name__ == '__main__':
    app.run(debug=True, port=8053)