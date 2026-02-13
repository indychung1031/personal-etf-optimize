import pandas as pd
import yfinance as yf
import data_loader

def test_single_ticker():
    ticker = "VOO"
    print(f"Testing load_stock_data with single ticker: {ticker}")
    data = data_loader.load_stock_data(ticker, period="1mo")
    
    print("Columns:", data.columns)
    print("Type:", type(data))
    
    if isinstance(data, pd.DataFrame) and ticker in data.columns:
        print("SUCCESS: Data is a DataFrame and contains the ticker column.")
    else:
        print("FAILURE: Data is not in the expected format.")
        print(data.head())

if __name__ == "__main__":
    test_single_ticker()
