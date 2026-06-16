# Quick Streamlit application

A simple Streamlit application to display stock market information with yfinance.

After installing Streamlit, start it with ``streamlit run streamlit_app.py``

## 1. Features
- Search stocks by ticker symbol or company name
  - Autocomplete stock suggestions while typing
- Display historical stock prices
- Select custom date ranges
  - Choose different data intervals (1 minute, 5 minutes, daily, weekly, monthly, etc.)
- Interactive candlestick chart
- Interactive price chart
- 20-period and 50-period moving averages
- Automatic anomaly detection based on price and volume changes
- Display volume and price-change indicators
- Financial metrics:
  - Total return
  - Volatility
  - Sharpe ratio
- Company financial statements
- Stock actions (dividends and stock splits)
- Compare two stocks on the same chart

## 2. Tech Stack
- **Python**
- **Streamlit**
- **yfinance**

## 3. Prerequisites
- Python 3.11+
- Streamlit, version 1.56.0.

## 4. Setup & Usage

Install the required dependencies:  
```pip install streamlit yfinance```  

As you can see from the project structure, the project is quite simple: You only have to launch the following command:  
```streamlit run streamlit_app.py```

## 6. Screenshots
In the box that appears on the front page, you will be suggested some stocks as soon as you insert something.

Select one to display Historical data, Financials and Stock Actions.
![Alt Text](screenshots/Screenshot_20260616_191701.png)   

You can also compare the stock with another stock, with the Select Box right below the first one.