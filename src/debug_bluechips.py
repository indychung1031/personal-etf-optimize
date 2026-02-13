import yfinance as yf

def debug_stocks(symbols):
    for symbol in symbols:
        print(f"\n--- {symbol} ---")
        t = yf.Ticker(symbol)
        info = t.info
        fast = t.fast_info
        print(f"Price: {info.get('currentPrice') or info.get('previousClose')}")
        print(f"Shares Outstanding: {info.get('sharesOutstanding')}")
        print(f"marketCap (info): {info.get('marketCap')}")
        print(f"market_cap (fast): {fast.get('market_cap')}")
        
        # Calculate manual
        price = info.get('currentPrice') or info.get('previousClose')
        shares = info.get('sharesOutstanding')
        if price and shares:
            print(f"Calculated: {price * shares}")

debug_stocks(["JPM", "WMT", "TSM", "AAPL"])
