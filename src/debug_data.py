import yfinance as yf
import json

def debug_ticker(symbol):
    print(f"\n--- Debugging: {symbol} ---")
    t = yf.Ticker(symbol)
    info = t.info
    fast = t.fast_info
    
    print(f"Currency: {info.get('currency')}")
    print(f"Market Cap (info): {info.get('marketCap')}")
    print(f"Market Cap (fast): {fast.get('market_cap')}")
    print(f"Total Assets (info): {info.get('totalAssets')}")
    print(f"Nav Price: {info.get('navPrice')}")
    print(f"Previous Close: {info.get('previousClose')}")

tickers = ["TSM", "SMH", "VOO", "2330.TW", "AIQ"]
for t in tickers:
    try:
        debug_ticker(t)
    except Exception as e:
        print(f"Error debugging {t}: {e}")
