# My Personal ETF Analyzer

This project allows you to design, simulate, and analyze your own custom ETF based on a curated pool of stocks from VOO, QQQ, and 9 key growth industries.

## Features
- **Master Stock Pool**: 150+ stocks consolidated from VOO, QQQ, and thematic ETFs (AI, Robotics, Space, etc.).
- **Portfolio Builder**: Select stocks and assign weights manually or use pre-defined templates.
- **Backtesting**: Simulate performance over the last 5 years and compare with VOO.
- **Analytics**: View CAGR, MDD, Sharpe Ratio, and sector allocation.

## How to Run

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Generate Stock Pool** (Already done, but if you update markdown files):
    ```bash
    python src/generate_stock_pool.py
    ```

3.  **Run the App**:
    ```bash
    streamlit run src/app.py
    ```

## Files
- `src/app.py`: Main application interface.
- `src/data_loader.py`: Fetches stock data from Yahoo Finance.
- `src/utils.py`: Calculates portfolio returns and metrics.
- `data/stock_pool.json`: The consolidated stock list.
