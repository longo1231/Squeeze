import requests
import pandas as pd
from datetime import datetime
import os

def fetch_squeeze_data():
    """
    Fetches latest data from SqueezeMetrics API and saves to Excel file
    """
    api_url = "https://squeezemetrics.com/monitor/api/latest?format=csv&key=0B7661B124724CA4C43BED7742F01266945A7B04BF698A758C9101727FE7392D"
    
    try:
        # Fetch data from API
        response = requests.get(api_url)
        response.raise_for_status()
        
        # Read CSV data into pandas DataFrame
        from io import StringIO
        df = pd.read_csv(StringIO(response.text))
        
        # Generate filename with current date
        current_date = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"squeeze_data_{current_date}.xlsx"
        
        # Save to Excel file
        df.to_excel(filename, index=False)
        
        print(f"Data successfully saved to {filename}")
        print(f"Records fetched: {len(df)}")
        return df
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from API: {e}")
        return None
    except Exception as e:
        print(f"Error processing data: {e}")
        return None

if __name__ == "__main__":
    fetch_squeeze_data()