import os
import re
import json

def parse_holdings():
    # Use relative paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    back_data_path = os.path.join(base_dir, '..', '..', 'back_data')
    data_dir = os.path.join(base_dir, '..', 'data')
    output_path = os.path.join(data_dir, 'etf_compositions.json')
    mapping_path = os.path.join(data_dir, 'ticker_mapping.json')
    pool_path = os.path.join(data_dir, 'stock_pool.json')
    
    # 1. Map files to ETFs
    files_map = {
        "voo_top20.md": ["VOO"],
        "qqq_top20.md": ["QQQ"],
        "thematic_holdings_tech.md": ["AIQ", "CHAT", "QTUM", "BOTZ", "ROBO", "SMH", "SOXX", "CIBR", "HACK"],
        "thematic_holdings_future.md": ["ARKX", "UFO", "ROKT", "DRIV", "IDRV"],
        "thematic_holdings_core.md": ["IBB", "XBI", "XME", "SETM", "PICK", "COPP"]
    }
    
    compositions = {}
    
    # Load centralized mapping
    name_to_ticker = {}
    if os.path.exists(mapping_path):
        with open(mapping_path, 'r', encoding='utf-8') as f:
            name_to_ticker = json.load(f)
            
    # Load master pool for additional mapping
    if os.path.exists(pool_path):
        with open(pool_path, 'r', encoding='utf-8') as f:
            pool = json.load(f)
            for p in pool:
                if p['name'] not in name_to_ticker:
                    name_to_ticker[p['name']] = p['ticker']

    for filename, etfs in files_map.items():
        path = os.path.join(back_data_path, filename)
        if not os.path.exists(path):
            print(f"File not found: {path}")
            continue
            
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        if "voo" in filename or "qqq" in filename:
            lines = content.split('\n')
            current_etf = "VOO" if "voo" in filename else "QQQ"
            compositions[current_etf] = {}
            
            for line in lines:
                if '|' in line and '%' in line:
                    parts = [p.strip() for p in line.split('|')]
                    if len(parts) >= 5:
                        # Rank | Company | Ticker | Weight |
                        # Use parts[4] for ticker since parts[0] is empty in | Rank | ...
                        # Depending on index, usually parts[4] is Ticker in qqq_voo_overlap
                        # However, voo_top20.md might be different. 
                        # Looking at qqq_voo header: | Rank (VOO) | Rank (QQQ) | Company | Ticker | Weight...
                        # parts: ['', ' 1 ', ' 1 ', ' NVIDIA Corp ', ' NVDA ', ...] -> NVDA is index 4
                        
                        # Default for voo_top20.md / qqq_top20.md
                        # | Rank | Company | Ticker | Weight (%) |
                        # parts: ['', Rank, Company, Ticker, Weight, '']
                        ticker = parts[3].strip()
                        
                        # Find weight - it's usually the one with %
                        weight = None
                        for p in parts:
                            if '%' in p:
                                try:
                                    # Handle cases like "0%*" or "7.74%"
                                    clean_w = p.replace('%', '').replace('*', '').strip()
                                    weight = float(clean_w)
                                    break
                                except:
                                    continue
                        
                        if ticker and weight is not None:
                            compositions[current_etf][ticker] = weight
        
        else:
            sections = content.split('### [')
            for section in sections[1:]:
                etf_code = section.split(']')[0].strip()
                compositions[etf_code] = {}
                
                lines = section.split('\n')
                for line in lines:
                    match = re.search(r'\d+\.\s+(.+?)\s+\((\d+\.\d+)%\)', line)
                    if match:
                        name = match.group(1).strip()
                        weight = float(match.group(2))
                        
                        ticker = name_to_ticker.get(name)
                        if not ticker:
                            # Heuristic fallbacks
                            if "NVIDIA" in name: ticker = "NVDA"
                            elif "Microsoft" in name: ticker = "MSFT"
                            elif "Apple" in name: ticker = "AAPL"
                            elif "Amazon" in name: ticker = "AMZN"
                            elif "Alphabet" in name: ticker = "GOOGL"
                            elif "Meta" in name: ticker = "META"
                            elif "Tesla" in name: ticker = "TSLA"
                            elif "Broadcom" in name: ticker = "AVGO"
                            else:
                                ticker = name
                        
                        compositions[etf_code][ticker] = weight

    # Save
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(compositions, f, indent=4)
        
    print(f"Saved compositions for {len(compositions)} ETFs to {output_path}")

if __name__ == "__main__":
    parse_holdings()
