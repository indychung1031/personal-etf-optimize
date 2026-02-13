import yfinance as yf
import json
import os

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def debug_full_system():
    base_dir = "C:/Users/indyc/Desktop/antigravity/project/Stock simulation/etf-analysis/myetf_project/data"
    compositions = load_json(os.path.join(base_dir, 'etf_compositions.json'))
    metadata = load_json(os.path.join(base_dir, 'etf_metadata.json'))
    
    tickers_to_check = ["TSM", "AMD", "CSCO", "CRWD", "INFY", "NVDA", "AAPL"]
    etf_tickers = list(metadata.keys())
    
    print("--- 1. Fetching Live AUMs ---")
    etf_aums = {}
    for etf in etf_tickers:
        try:
            t = yf.Ticker(etf)
            # Use totalAssets for ETFs
            aum = t.info.get('totalAssets')
            if aum is None:
                aum = t.info.get('marketCap', 0)
            etf_aums[etf] = aum / 1e9 # Billion
            print(f"{etf}: ${etf_aums[etf]:.2f}B")
        except:
            print(f"{etf}: ERROR")
            etf_aums[etf] = 0.0

    print("\n--- 2. Analyzing Weight Components ---")
    total_market_consensus = 0
    stock_scores = {}
    
    for etf, holdings in compositions.items():
        aum = etf_aums.get(etf, 0)
        for ticker, weight_in_etf in holdings.items():
            contribution = aum * (weight_in_etf / 100.0)
            stock_scores[ticker] = stock_scores.get(ticker, 0) + contribution
            total_market_consensus += contribution

    for stock in tickers_to_check:
        print(f"\nStock: {stock}")
        score = stock_scores.get(stock, 0)
        final_weight = (score / total_market_consensus * 100) if total_market_consensus > 0 else 0
        
        # Detail sources
        for etf, holdings in compositions.items():
            if stock in holdings:
                w = holdings[stock]
                aum = etf_aums.get(etf, 0)
                print(f"  - {etf}: {w}% in ${aum:.2f}B -> {aum*(w/100):.4f} score")
        
        print(f"Total Raw Score: {score:.4f}")
        print(f"Final Percentage: {final_weight:.4f}%")

if __name__ == "__main__":
    debug_full_system()
