import yfinance as yf
import pandas as pd

def test_reliability(symbols):
    for s in symbols:
        print(f"\n--- {s} ---")
        t = yf.Ticker(s)
        info = t.info
        
        # 1. Info Price
        p_info = info.get('currentPrice') or info.get('previousClose')
        
        # 2. History Price
        hist = t.history(period="5d")
        p_hist = hist['Close'].iloc[-1] if not hist.empty else None
        
        # 3. Market Cap from Info
        m_info = info.get('marketCap')
        
        # 4. Market Cap from FastInfo
        m_fast = t.fast_info.get('market_cap')
        
        # 5. Shares
        shares = info.get('sharesOutstanding')
        
        print(f"Price (info): {p_info}")
        print(f"Price (hist): {p_hist}")
        print(f"Shares: {shares}")
        print(f"Mcap (info): {m_info}")
        print(f"Mcap (fast): {m_fast}")
        if p_hist and shares:
             print(f"Calculated (hist * shares): {p_hist * shares}")

test_reliability(["WMT", "TSM", "JPM", "AAPL", "NVDA"])
