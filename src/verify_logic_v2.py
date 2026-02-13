import json
import os

def verify_logic_2_0():
    # Load data from myetf_project/data (assuming current working directory is myetf_project)
    try:
        with open('data/etf_metadata.json', 'r', encoding='utf-8') as f:
            etf_metadata = json.load(f)
        with open('data/etf_compositions.json', 'r', encoding='utf-8') as f:
            compositions = json.load(f)
    except FileNotFoundError:
        # Fallback for running from parent directory
        with open('myetf_project/data/etf_metadata.json', 'r', encoding='utf-8') as f:
            etf_metadata = json.load(f)
        with open('myetf_project/data/etf_compositions.json', 'r', encoding='utf-8') as f:
            compositions = json.load(f)

    etf_aums = {k: v['fallback_aum'] for k, v in etf_metadata.items()}
    
    stock_raw_scores = {}
    stock_breakdown = {}
    
    for etf, aum in etf_aums.items():
        if etf in compositions:
            limit = 20 if etf in ["VOO", "QQQ"] else 10
            sorted_holdings = sorted(compositions[etf].items(), key=lambda x: x[1], reverse=True)[:limit]
            
            for t, w in sorted_holdings:
                raw_score = aum * (w / 100.0)
                stock_raw_scores[t] = stock_raw_scores.get(t, 0) + raw_score
                if t not in stock_breakdown: stock_breakdown[t] = {}
                stock_breakdown[t][etf] = raw_score

    total_pool_cap = sum(stock_raw_scores.values())
    final_weights = {t: (v / total_pool_cap) * 100 for t, v in stock_raw_scores.items()}
    
    print(f"--- Logic 2.0 Verification (Total Pool Capital: ${total_pool_cap:.2f}B) ---")
    print(f"{'Ticker':<8} | {'Weight (%)':<10} | {'Sources'}")
    print("-" * 50)
    
    sorted_weights = sorted(final_weights.items(), key=lambda x: x[1], reverse=True)
    for t, w in sorted_weights[:30]: # Show top 30
        sources = ", ".join([f"{k}(${v:.1f}B)" for k, v in stock_breakdown[t].items()])
        print(f"{t:<8} | {w:<10.4f} | {sources}")

if __name__ == "__main__":
    verify_logic_2_0()
