
from datetime import date, timedelta

import streamlit as st
from streamlit_extras.mandatory_date_range import date_range_picker
import yfinance as yf
import pandas as pd

from streamlit_searchbox import st_searchbox

import plotly.graph_objects as go

# @TODO: Styling for the elements in the searchbar
# @TODO: Workaround to display nicely and return efficiently
# Thought: Maybe parse the string once received. I need only the symbol after all
# @TODO: Error when no result - check on that - That might be because the value for symbols was retrieved without get
# @TODO: Check if the numbers (millions) could be more readable
def search_function(searchterm: str):
    if not searchterm:
        return []
    tickers = yf.Search(searchterm, max_results=10).quotes

    return [
        # {"Symbol": i.get('symbol'), "Short name": i.get('shortname')} for i in tickers
        {"Symbol": i.get('symbol'), "Short name": i.get('shortname'), "Long name": i.get('longname')} for i in tickers
    ]

def interval_select_box(start_date, end_date):
    # https://algotrading101.com/learn/yfinance-guide/
    # However it is important to note that the 1m data is only retrievable for the last 7 days,
    # and anything intraday (interval <1d) only for the last 60 days

    basic_options = ("One Day", "One Week", "One Month")

    if end_date - start_date <= timedelta(days=7):
        basic_options = (
            'One Minute', 'Two Minutes', 'Three Minutes', 'Fifteen Minutes',
            'Thirty Minutes', 'One Hour', 'Ninety Minutes'
        ) + basic_options
    elif end_date - start_date <= timedelta(days=60):
        basic_options = (
            'Two Minutes', 'Three Minutes', 'Fifteen Minutes',
            'Thirty Minutes', 'One Hour', 'Ninety Minutes',
        ) + basic_options

    option = st.selectbox(
        "Select an interval for the historical data", basic_options,
        help="The 1-minute data is only retrievable for the last 7 days, and anything intraday (inferior to 1 day) only for the last 60 days"
    )

    interval_translator = {
        'One Day': '1d',
        'One Week': '1wk',
        'One Month': '1mo',
        'One Minute': '1m',
        'Two Minutes': '2m',
        'Three Minutes': '5m',
        'Fifteen Minutes': '15m',
        'Thirty Minutes': '30m',
        'One Hour': '60m',
        'Ninety Minutes': '90m'
    }
    st.write(interval_translator[option])

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

    # Display a summary of the fetched data
    # @TODO: Do so that you retrieve enough data to calculate the starting values
    st.write("Historical Data:", hd[['Open', 'High', 'Low', 'Close', 'Volume']].iloc[::-1])

    # 20-Day and 50-Day Moving Averages
    hd["MA20"] = hd["Close"].rolling(window=20).mean()
    hd["MA50"] = hd["Close"].rolling(window=50).mean()

    st.write("Other values", hd[['Dividends', 'Stock Splits', 'MA20', 'MA50']].iloc[::-1])

    # Build a figure with plotly. A bit different from the YT tutorial
    # new_frame = pd.DataFrame(historical_data)
    # fig = go.Figure(data=[go.Candlestick(x=new_frame.index,
    #                                      open=new_frame['Open'], high=new_frame['High'],
    #                                      low=new_frame['Low'], close=new_frame['Close'])])
    # st.plotly_chart(fig)
    hd["price_change"] = hd["Close"].pct_change()  # daily % change

    hd["z_volume"] = (hd["Volume"] - hd["Volume"].mean()) / hd["Volume"].std()
    hd["z_price"] = (hd["price_change"] - hd["price_change"].mean()) / hd["price_change"].std()

    # @TODO: You can zoom on charts. but the problem is, you do not control how you can zoom.
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=hd.index, y=hd['Close'],
                              mode='lines',
                              name='Close Price', line=dict(color='green')))
    fig2.add_trace(go.Scatter(x=hd.index, y=hd['MA20'],
                              mode='lines',
                              name='20-Day Moving Averages', line=dict(color='orange')))
    fig2.add_trace(go.Scatter(x=hd.index, y=hd['MA50'],
                              mode='lines',
                              name='50-Day Moving Averages', line=dict(color='blue')))
    if interval is "1d":
        # Flag a day as anomalous if either Z-score exceeds 2
        hd["anomaly"] = (hd["z_volume"].abs() > 2) | (hd["z_price"].abs() > 2)
        anomalies = hd[hd["anomaly"] == True]
        anomalies["hover_text"] = (
                "Z-volume: " + hd["z_volume"].round(2).astype(str) + "<br>" +
                "Z-price: " + hd["z_price"].round(2).astype(str)
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

    # st.write("Volumes")
    #
    # # Which sometimes makes the charts harder to read. We should at least try to do something about it.
    # volume_chart = go.Figure()
    # volume_chart.add_trace(go.Scatter(x=historical_data.index, y=historical_data['Volume'],
    #                                   mode='lines',
    #                                   name='Volume', line=dict(color='blue')))
    # st.plotly_chart(volume_chart)

def get_financial_data(symbol: str):

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

selected_value = st_searchbox(
    search_function,
    placeholder="Search...",
    key="search_box",
    debounce=250  # Delays callback by 250ms
)

if selected_value:

    st.write(f"<p style=\"color: royalblue;font-size: 20px;text-align: center\"><b>{selected_value.get("Symbol")} | {selected_value.get("Short name")} | {selected_value.get("Long name")}</b></p>",
             unsafe_allow_html=True)

    historical_data_tab, financials_tab, stock_actions_tab = st.tabs(["Historical Data", "Financials", "Stock Actions"])

    get_financial_data(selected_value.get("Symbol"))
