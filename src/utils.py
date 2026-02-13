import pandas as pd
import numpy as np

def calculate_portfolio_returns(weights, price_data):
    """
    Calculates the portfolio's cumulative return and daily returns.
    
    Args:
        weights (dict): Dictionary of {ticker: weight} (e.g., {'AAPL': 0.1, ...})
        price_data (pd.DataFrame): DataFrame of historical close prices (index=Date, columns=Tickers)
        
    Returns:
        pd.Series: Portfolio cumulative return series
        pd.Series: Portfolio daily return series
    """
    # Ensure weights sum to 1 (or allow leverage? For now normalize or assume user handled it)
    # Filter price data to only include tickers in weights
    available_tickers = [t for t in weights.keys() if t in price_data.columns]
    
    if not available_tickers:
        return pd.Series(), pd.Series()
        
    subset_data = price_data[available_tickers].dropna()
    
    # Calculate daily returns
    daily_returns = subset_data.pct_change().dropna()
    
    # Portfolio daily return = sum(weight * daily_return for each stock)
    # Align weights with the columns
    
    weighted_returns = daily_returns[available_tickers].mul([weights[t] for t in available_tickers], axis=1)
    portfolio_daily_ret = weighted_returns.sum(axis=1)
    
    # Cumulative return
    portfolio_cum_ret = (1 + portfolio_daily_ret).cumprod() - 1
    
    return portfolio_cum_ret, portfolio_daily_ret

def calculate_metrics(daily_returns):
    """
    Calculates CAGR, MDD, Sharpe Ratio.
    """
    if daily_returns.empty:
        return {}
        
    # CAGR
    total_days = len(daily_returns)
    years = total_days / 252
    total_return = (1 + daily_returns).prod() - 1
    cagr = (1 + total_return) ** (1 / years) - 1
    
    # MDD
    cumulative = (1 + daily_returns).cumprod()
    peak = cumulative.cummax()
    drawdown = (cumulative - peak) / peak
    mdd = drawdown.min()
    
    # Sharpe (assuming risk-free rate ~ 4% or 0 for simplicity in comparison)
    rf = 0.04
    excess_ret = daily_returns.mean() * 252 - rf
    volatility = daily_returns.std() * np.sqrt(252)
    sharpe = excess_ret / volatility if volatility != 0 else 0
    
    return {
        "CAGR": cagr,
        "MDD": mdd,
        "Sharpe": sharpe,
        "Total Return": total_return
    }

def calculate_consolidated_weights(etf_aums, compositions):
    """
    Centralized Logic 2.0: Calculates consolidated stock weights based on ETF AUMs.
    Following Step 3-7 of the investment strategy.
    
    Returns:
        dict: {ticker: weight_percentage}
        dict: {ticker: {etf: raw_score}} (for breakdown details)
    """
    stock_raw_scores = {}
    stock_breakdown = {}
    
    for etf, aum in etf_aums.items():
        if etf in compositions:
            # Step 3-5: Top 20 for Index, Top 10 for Themes
            limit = 20 if etf in ["VOO", "QQQ"] else 10
            
            # Sort to guarantee Top N
            top_holdings = sorted(compositions[etf].items(), key=lambda x: x[1], reverse=True)[:limit]
            
            for t, w in top_holdings:
                # Raw Score = Allocated Capital in Billion USD
                raw_score = aum * (w / 100.0)
                
                stock_raw_scores[t] = stock_raw_scores.get(t, 0) + raw_score
                
                if t not in stock_breakdown:
                    stock_breakdown[t] = {}
                stock_breakdown[t][etf] = raw_score

    # Global Normalization
    total_raw_score = sum(stock_raw_scores.values())
    final_weights = {}
    
    if total_raw_score > 0:
        for t, score in stock_raw_scores.items():
            final_weights[t] = (score / total_raw_score) * 100
            
    return final_weights, stock_breakdown
