import data_loader
import json

def verify():
    tickers = ["TSM", "SMH", "VOO", "9412.T", "6285.TW"]
    print(f"Verifying tickers: {tickers}")
    caps = data_loader.get_market_caps(tickers)
    
    for t in tickers:
        val = caps.get(t)
        if val:
            print(f"{t}: ${val/1e9:,.2f} Billion")
        else:
            print(f"{t}: DATA FAILED")

if __name__ == "__main__":
    verify()
