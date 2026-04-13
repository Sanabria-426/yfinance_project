
from datetime import date, timedelta

import pandas as pd
import plotly.graph_objects as go
import yfinance as yf
import streamlit as st
from streamlit_extras.mandatory_date_range import date_range_picker
from streamlit_searchbox import st_searchbox

def search_function(searchterm: str) -> list[tuple[str, dict]]:
    if not searchterm:
        return []
    tickers = yf.Search(searchterm, max_results=10).quotes

    return [(
        f"Symbol: {i.get('symbol')} | Short name: {i.get('shortname')}",
        i
    ) for i in tickers ]

def interval_select_box(start_date, end_date):
    # https://algotrading101.com/learn/yfinance-guide/
    # However it is important to note that the 1m data is only retrievable for the last 7 days,
    # and anything intraday (interval <1d) only for the last 60 days

    basic_options = ("One Day", "One Week", "One Month")
    index=0

    if end_date - start_date <= timedelta(days=7):
        basic_options = (
            'One Minute', 'Two Minutes', 'Five Minutes', 'Fifteen Minutes',
            'Thirty Minutes', 'One Hour', 'Ninety Minutes'
        ) + basic_options
        index=7
    elif end_date - start_date <= timedelta(days=60):
        basic_options = (
            'Two Minutes', 'Five Minutes', 'Fifteen Minutes',
            'Thirty Minutes', 'One Hour', 'Ninety Minutes',
        ) + basic_options
        index=6
    option = st.selectbox(
        "Select an interval for the historical data", basic_options, index=index,
        help="The 1-minute data is only retrievable for the last 7 days, and anything intraday (inferior to 1 day) only for the last 60 days"
    )

    interval_translator = {
        'One Minute': '1m',
        'Two Minutes': '2m',
        'Five Minutes': '5m',
        'Fifteen Minutes': '15m',
        'Thirty Minutes': '30m',
        'One Hour': '60m',
        'Ninety Minutes': '90m',
        'One Day': '1d',
        'One Week': '1wk',
        'One Month': '1mo'
    }

    return interval_translator[option]

@st.fragment(run_every="1m")
def get_historical_data(ticker):
    start_date, end_date = date_range_picker(
        "Select a range for the historical data",
        default_start=date.today() - timedelta(days=30),
        default_end=date.today(),
        min_date=date(1970, 1, 1),
        max_date=date.today(),
        error_message="Please select start and end date"
    )
    interval = interval_select_box(start_date, end_date)

    # Historical Data: hd
    hd = ticker.history(start=start_date, end=end_date + timedelta(days=1), interval=interval)

    if interval in ('1d', '1wk', '1mo'):
        # Why such a timedelta? Because there are more calendar days than business days.
        # 50 business days generally means 72 days top. Going to 100 is a bit of an overkill.
        hd_for_moving_averages = ticker.history(start=start_date - timedelta(days=100), end=end_date + timedelta(days=1), interval=interval)

        # 20-Day and 50-Day Moving Averages
        ma = hd_for_moving_averages["Close"].rolling(window=20).mean()
        hd["MA20"] = ma.reindex(hd.index)

        ma = hd_for_moving_averages["Close"].rolling(window=50).mean()
        hd["MA50"] = ma.reindex(hd.index)

    if interval not in ('1d', '1wk', '1mo'):
        st.write(f"<p style=\"color: red;font-size: 12;\">We cannot compute Moving Averages for this interval, as well as Anomalies.\n"
                 "To display such information, the interval should be superior or equal to 1 day.</p>",
             unsafe_allow_html=True)

    # Display a summary of the fetched data
    st.write("Historical Data:", hd[['Open', 'High', 'Low', 'Close', 'Volume']].iloc[::-1])

    try:
        st.write("Other values", hd[['Dividends', 'Stock Splits', 'MA20', 'MA50']].iloc[::-1])
    except KeyError:
        st.write("Dividends and Stock Splits cannot be displayed for this time interval.")

    hd["price_change"] = hd["Close"].pct_change()  # daily % change
    hd["z_volume"] = (hd["Volume"] - hd["Volume"].mean()) / hd["Volume"].std()
    hd["z_price"] = (hd["price_change"] - hd["price_change"].mean()) / hd["price_change"].std()

    fig = go.Figure(data=[go.Candlestick(
        x=hd.index,
        open=hd['Open'],
        high=hd['High'],
        low=hd['Low'],
        close=hd['Close'],
        name="Candlesticks"
    )])
    st.plotly_chart(fig)


    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=hd.index, y=hd['Close'],
                              mode='lines',
                              name='Close Price', line=dict(color='green')))

    if interval in ('1d', '1wk', '1mo'):
        fig2.add_trace(go.Scatter(x=hd.index, y=hd['MA20'],
                                  mode='lines',
                                  name='20-Day Moving Averages', line=dict(color='orange')))
        fig2.add_trace(go.Scatter(x=hd.index, y=hd['MA50'],
                                  mode='lines',
                                  name='50-Day Moving Averages', line=dict(color='blue')))
    # Kept the chart readable by disabling anomalies for a very short interval
    # In two different ifs, as the code is in this conditional for another reason
    if interval in ('1d', '1wk', '1mo'):
        # Flag a day as anomalous if either Z-score exceeds 2
        hd["anomaly"] = (hd["z_volume"].abs() > 2) | (hd["z_price"].abs() > 2)

        anomalies = hd[hd["anomaly"] == True].copy()
        anomalies["hover_text"] = (
                "Z-volume: " + anomalies["z_volume"].round(2).astype(str) + "<br>" +
                "Z-price: " + anomalies["z_price"].round(2).astype(str)
        )

        fig2.add_trace(go.Scatter(x=anomalies.index, y=anomalies["Close"],
            mode="markers", name="Anomaly", marker=dict(color="red", size=5, symbol="circle"),
            text=anomalies["hover_text"],
            hoverinfo="text+x+y",
        ))
    st.plotly_chart(fig2)

    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=hd.index, y=hd['z_volume'],
                              mode='lines',
                              name='Daily Volumes', line=dict(color='blue')))
    fig3.add_trace(go.Scatter(x=hd.index, y=hd['z_price'],
                              mode='lines',
                              name='Daily Price Change', line=dict(color='green')))
    st.plotly_chart(fig3)

def get_financial_data(symbol: str):

    try:
        ticker = yf.Ticker(symbol)
        with historical_data_tab:
            get_historical_data(ticker)

        # Fetch basic financials
        with financials_tab:
            financials = ticker.financials
            st.write("\nFinancials:")
            st.write(financials)

        # Fetch stock actions like dividends and splits
        with stock_actions_tab:
            actions = ticker.actions
            st.write("\nStock Actions:")
            st.write(actions)
    except Exception:
        st.write(f'A problem occurred while retrieving data for this symbol: {symbol}')

selected_value = st_searchbox(
    search_function,
    placeholder="Search...",
    key="search_box",
    debounce=250
)

if selected_value:

    st.write(f"<p style=\"color: royalblue;font-size: 20px;text-align: center\"><b>{selected_value.get("symbol")} | {selected_value.get("shortname")} | {selected_value.get("longname")}</b></p>",
             unsafe_allow_html=True)

    historical_data_tab, financials_tab, stock_actions_tab = st.tabs(["Historical Data", "Financials", "Stock Actions"])

    get_financial_data(selected_value.get("symbol"))
