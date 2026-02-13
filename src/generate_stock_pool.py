import json
import os
import re

def parse_markdown_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract ticker and company name using regex
    # Matches lines like: | **NVDA** | NVIDIA Corp | ...
    # Or list items like: 1. Samsung Electronics (5.99%) -> difficult to get ticker
    # Or list items like: 1. Alphabet Inc (A) (4.60%) -> difficult
    
    # Strategy: Focus on the Master Stock Pool table first, 
    # then iterate through thematic files if possible, but thematic files don't have tickers consistently.
    # The thematic files have "Company Name (Ticker)" format? No, they have "1. Samsung Electronics (5.99%)"
    # Wait, the thematic files do NOT have tickers in the list items!
    # Ah, the `sector_overlap_analysis.md` has tickers for ETFs, but not holdings.
    # The `master_stock_pool.md` has tickers for the frequency table. 
    # The `qqq_voo_overlap_analysis.md` has tickers!
    
    # For now, let's just parse the `master_stock_pool.md` table which seems to have the most "important" ones.
    # If we need more, we might need to use a library or just manual mapping, or asking the user.
    # The user said "150+ stocks", so I should try to get as many as possible.
    # `qqq_voo_overlap_analysis.md` has a table with Tickers.
    # `master_stock_pool.md` has a table with Tickers.
    
    stocks = {}
    
    # Regex for markdown table row with Ticker in first or second column
    # | Rank | Rank | Company | Ticker | ... (qqq_voo)
    # | Ticker | Company Name | Frequency | ... (master_stock_pool)
    
    lines = content.split('\n')
    for line in lines:
        if '|' not in line:
            continue
        parts = [p.strip() for p in line.split('|')]
        if len(parts) < 3:
            continue
            
        # Check for Ticker column content
        # Heuristic: Ticker is usually 1-5 chars, uppercase.
        
        # Try to find a ticker-like string in the parts
        ticker = None
        company = None
        
        for part in parts:
            # Remove ** bold markers
            clean_part = part.replace('*', '').strip()
            if not clean_part:
                continue
                
            # If it matches Ticker pattern (1-5 uppercase letters, maybe . or -)
            if re.match(r'^[A-Z]{1,5}(\.[A-Z])?$', clean_part) and clean_part not in ['VOO', 'QQQ', 'ETF', 'AI', 'EV', 'Rank']:
                 # Avoid column headers
                 if clean_part in ['Ticker', 'Symbol', 'Rank']:
                     continue
                 ticker = clean_part
                 break
        
        if ticker:
            # Try to find company name
            # Usually the longest string in the row is the company name? 
            # Or the one next to the ticker?
            # Let's look for a name-like string
            for part in parts:
                clean_part = part.replace('*', '').strip()
                if clean_part and clean_part != ticker and len(clean_part) > 2 and not re.match(r'^\d+(\.\d+)?%?$', clean_part) and not re.match(r'^\d+$', clean_part):
                     # Exclude numbers, percentages
                     if clean_part not in ['Company', 'Name', 'Frequency', 'Source / Sectors', 'Weight', 'Integrated']:
                         company = clean_part
                         break
            
            if ticker and company:
                stocks[ticker] = {
                    'name': company,
                    'ticker': ticker,
                    'sector': 'Unknown' # We can populate sector if available in the row
                }
                
                # Try to extract Frequency or Source from master pool
                if 'Frequency' in content: 
                     # This is master stock pool file
                     # Last column usually has sources
                     if len(parts) > 4:
                         stocks[ticker]['sources'] = parts[-1].strip()
                         
    return stocks

def main():
    # Use relative paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    base_path = os.path.join(base_dir, '..', '..', 'back_data')
    output_path = os.path.join(base_dir, '..', 'data', 'stock_pool.json')
    
    files_to_parse = [
        "master_stock_pool.md",
        "qqq_voo_overlap_analysis.md"
    ]
    
    all_stocks = {}
    
    for filename in files_to_parse:
        file_path = os.path.join(base_path, filename)
        if os.path.exists(file_path):
            print(f"Parsing {filename}...")
            stocks = parse_markdown_file(file_path)
            all_stocks.update(stocks)
            
    # Convert to list
    stock_list = list(all_stocks.values())
    
    # Save to JSON
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(stock_list, f, indent=4)
        
    print(f"Extracted {len(stock_list)} stocks to {output_path}")

if __name__ == "__main__":
    main()
