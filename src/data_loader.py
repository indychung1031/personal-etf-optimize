import yfinance as yf
import pandas as pd
import streamlit as st
import os
import json
import concurrent.futures

# Load ticker mapping from JSON
def load_ticker_mapping():
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        mapping_path = os.path.join(base_dir, '..', 'data', 'ticker_mapping.json')
        with open(mapping_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

NAME_TO_TICKER = load_ticker_mapping()

def normalize_ticker(ticker):
    """
    Normalizes a ticker symbol or company name to a valid Yahoo Finance ticker.
    Handles 'BRK.B' -> 'BRK-B' and maps names to tickers.
    """
    if not isinstance(ticker, str):
        return ticker
        
    t = ticker.strip()
    
    # 1. Check Explicit Mapping (Names -> Ticker)
    if t in NAME_TO_TICKER:
        return NAME_TO_TICKER[t]
        
    # 2. Handle Common Variations
    t_upper = t.upper()
    if 'BRK.B' in t_upper:
        return t_upper.replace('BRK.B', 'BRK-B')
    
    # 3. Default (Assume it is a ticker if not mapped)
    return t_upper

@st.cache_data(ttl=3600*24) # Cache data for 24 hours
def load_stock_data(tickers, period="5y", interval="1d"):
    """
    Fetches historical stock data for the given tickers.
    """
    if isinstance(tickers, list):
        tickers = " ".join(tickers)
    
    try:
        # Download data
        # auto_adjust=True returns 'Close' which is actually Adj Close. 
        # For multiple tickers, it returns MultiIndex columns (Price, Ticker) by default? 
        # No, by default it groups by Column (Open, Close...), then Ticker. 
        # So data['Close'] gives a DF with tickers as columns.
        
        data = yf.download(tickers, period=period, interval=interval, auto_adjust=True, progress=False)
        
        if data.empty:
            return pd.DataFrame()

        # Check structure
        if "Close" in data.columns:
            return data["Close"]
        
        # If single ticker and auto_adjust=True, it might just have 'Close' as a column (not MultiIndex)
        # If multiple tickers, data['Close'] works.
        
        # Fallback for checking if the columns are just the price data directly (rare with recent yfinance)
        # Sometime yf returns columns like "Ticker" level if we use group_by='ticker'
        
        # Let's handle the case where 'Close' might be missing but 'Adj Close' is there (if auto_adjust=False)
        if "Adj Close" in data.columns:
            return data["Adj Close"]

        # If we are here, we might have a single ticker dataframe that IS just the OHLC data
        # If it has a 'Close' column itself (not under a level), return it as a Series/DataFrame
        # But we need to ensure we return a DataFrame with the ticker name if it's a Series
        
        # Simply return the 'Close' column if present at top level logic failed above
        # With current yfinance, if we ask for "NVDA", we get columns Open, High, Low, Close, Volume
        # data['Close'] gives a Series. We want a DataFrame with column name "NVDA".
        
        # Re-evaluating:
        # If we ask for multiple tickers, data['Close'] is a DataFrame with columns=Tickers. Perfect.
        # If we ask for single ticker "VOO", data['Close'] is a Series named 'Close'.
        # We want to convert that Series to a DataFrame with column "VOO".
        
        if isinstance(data.columns, pd.MultiIndex):
            # It's likely headers are (Price, Ticker) or (Ticker, Price). 
            # If standard download: (Price, Ticker). 
            # data['Close'] should work.
            if 'Close' in data.columns.get_level_values(0):
                 pass # data['Close'] will work
        else:
             # Single level columns
             pass
             
        # Safe extraction
        if 'Close' in data:
            prices = data['Close']
            # If it's a Series (single ticker), convert to DF with ticker name
            if isinstance(prices, pd.Series):
                prices = prices.to_frame()
                prices.columns = [tickers.strip()]
            return prices
            
        return pd.DataFrame()

    except Exception as e:
        # Don't show error to user immediately, just return empty so app can handle
        print(f"Debug Error fetching {tickers}: {e}") 
        return pd.DataFrame()
        
    except Exception as e:
        # st.error(f"Error fetching data: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=300) # Cache for 5 minutes
def get_latest_prices(tickers):
    """
    Fetches the latest available closing price for the given tickers.
    Uses ThreadPoolExecutor for robustness against batch download failures.
    Returns a dictionary {ORIGINAL_TICKER: price}. 
    Note: The key in the returned dict must MATCH the input ticker (even if it's a name) 
    so the app can look it up.
    """
    if not tickers:
        return {}
        
    prices = {}
    
    # Create list of (Original, Normalized) tuples
    if isinstance(tickers, list):
         ticker_pairs = [(t, normalize_ticker(t)) for t in tickers if isinstance(t, str)]
    else:
         ticker_pairs = [(t, normalize_ticker(t)) for t in tickers.split()]
    
    # Unique pairs to avoid blocking on duplicates
    unique_pairs = list(set(ticker_pairs))
    
    def fetch_price(original, normalized):
        try:
            dat = yf.Ticker(normalized)
            p = dat.fast_info.get('last_price', None)
            if p is None:
                p = dat.fast_info.get('previous_close', None)
            
            if p is None:
                hist = dat.history(period="1d")
                if not hist.empty:
                    p = hist['Close'].iloc[-1]
            
            return original, p
        except Exception as e:
            return original, None

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        future_to_ticker = {executor.submit(fetch_price, orig, norm): orig for orig, norm in unique_pairs}
        
        for future in concurrent.futures.as_completed(future_to_ticker):
            t, p = future.result()
            if p and p > 0:
                prices[t] = p
            
    return prices

import concurrent.futures

@st.cache_data(ttl=3600*24) # Cache for 24 hours
def get_market_caps(tickers):
    if not tickers:
        return {}
    
    market_caps = {}
    
    # Create list of (Original, Normalized) tuples
    if isinstance(tickers, list):
         ticker_pairs = [(t, normalize_ticker(t)) for t in tickers if isinstance(t, str)]
    else:
         ticker_pairs = [(t, normalize_ticker(t)) for t in tickers.split()]
    
    # Unique pairs
    unique_pairs = list(set(ticker_pairs))
    
    # Fallback map for tickers with missing market cap data in Yahoo (e.g. ADRs)
    MCAP_FALLBACKS = {
        "ABB": "ABBN.SW",
    }

    # Approximated exchange rates (Target: USD)
    EXCHANGE_RATES = {
        "JPY": 1/150.0,
        "TWD": 1/32.0,
        "KRW": 1/1350.0,
        "EUR": 1.08,
        "GBP": 1.26,
        "CAD": 0.74,
        "HKD": 0.128,
        "AUD": 0.65,
        "CHF": 1.13,
        "PLN": 0.25,
        "MXN": 0.058,
        "SAR": 0.27
    }

    def get_stable_mcap(ticker_obj, info):
        """Cross-checks marketCap with Price * Shares to avoid Yahoo noise."""
        try:
            mcap_raw = info.get('marketCap')
            price = info.get('currentPrice') or info.get('previousClose')
            shares = info.get('sharesOutstanding')
            
            if price and shares:
                calculated_cap = price * shares
                if mcap_raw:
                    # If discrepancy > 10% (Scale error), trust the calculated value
                    if abs(mcap_raw - calculated_cap) / calculated_cap > 0.1:
                        return calculated_cap
                return calculated_cap if calculated_cap > 0 else mcap_raw
            return mcap_raw
        except:
            return info.get('marketCap')

    def fetch_cap(original, normalized):
        cap = None
        currency = "USD"
        try:
            ticker_obj = yf.Ticker(normalized)
            
            # 1. Try Fast Info first (Much faster and less likely to be blocked in Cloud)
            try:
                f_info = ticker_obj.fast_info
                cap = f_info.get('market_cap') or f_info.get('total_assets')
                currency = f_info.get('currency', 'USD')
            except:
                pass

            # 2. If Fast Info failed or returned nothing, try full .info as fallback
            if cap is None:
                try:
                    info = ticker_obj.info
                    quote_type = info.get('quoteType', '').upper()
                    if quote_type == 'ETF':
                        cap = info.get('totalAssets') or info.get('marketCap')
                    else:
                        cap = get_stable_mcap(ticker_obj, info)
                    currency = info.get('currency', 'USD')
                except:
                    pass
            
            # Simple TSM double counting check
            if normalized == "TSM" and cap and cap > 1.5e12:
                cap = cap / 2.0

            # 3. Try Explicit Fallback (e.g. Swiss ticker for ABB)
            if cap is None and normalized in MCAP_FALLBACKS:
                fb_ticker = MCAP_FALLBACKS[normalized]
                try:
                    fb_obj = yf.Ticker(fb_ticker)
                    cap = fb_obj.fast_info.get('market_cap')
                    currency = fb_obj.fast_info.get('currency', 'USD')
                except:
                    pass
            
            # 4. Currency Conversion
            if cap and currency != "USD":
                rate = EXCHANGE_RATES.get(currency, 1.0)
                cap = cap * rate

            return original, cap
        except Exception:
            return original, None

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        future_to_ticker = {executor.submit(fetch_cap, orig, norm): orig for orig, norm in unique_pairs}
        
        for future in concurrent.futures.as_completed(future_to_ticker):
            t, cap = future.result()
            if cap and cap > 0:
                market_caps[t] = cap
            
    return market_caps
    
def load_stock_pool():
    """
    Loads the master stock pool from the JSON file.
    """
    file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'stock_pool.json')
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_sector_map():
    """
    Returns a dictionary mapping tickers to their primary sector/theme.
    """
    pool = load_stock_pool()
    sector_map = {}
    for stock in pool:
        # Simple heuristic: use the first source as the "primary" sector for now
        # logic can be improved later
        sources = stock.get('sources', 'Unknown')
        primary_sector = sources.split(',')[0].strip()
        sector_map[stock['ticker']] = primary_sector
    return sector_map
