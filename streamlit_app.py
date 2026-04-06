
from datetime import date, timedelta

import streamlit as st
from streamlit_extras.mandatory_date_range import date_range_picker
import yfinance as yf
import pandas as pd

from streamlit_searchbox import st_searchbox

import plotly.graph_objects as go

def search_function(searchterm: str):
    if not searchterm:
        return []
    tickers = yf.Search(searchterm, max_results=10).quotes
    # @TODO: Styling for the elements in the searchbar
    # @TODO: Workaround to display nicely and return efficiently
    # Thought: Maybe parse the string once received. I need only the symbol after all
    # @TODO: Error when no result - check on that
    # @TODO: Check if the numbers (millions) could be more readable

    return [
        {"Symbol": i.get('symbol'), "Short name": i.get('shortname')}
    for i in tickers ]

# @TODO: Maybe provide a sidebar for the user to clearly identify what is displayed
def get_financial_data(symbol: str):
    # Create a Ticker object
    ticker = yf.Ticker(symbol)

    # Fetch historical market data for the last year

    start_date, end_date = date_range_picker(
        "Select a range for the historical data",
        default_start=date.today() - timedelta(days=30),
        default_end=date.today(),
        min_date=date(1970, 1, 1),
        max_date=date.today(),
        error_message="Please select start and end date"
    )

    st.write(start_date, end_date)

    historical_data = ticker.history(start=start_date, end=end_date)

    # Display a summary of the fetched data
    st.write("Historical Data:")
    st.write(historical_data[['Open', 'High', 'Low', 'Close', 'Volume']])

    # Build a figure with plotly. A bit different from the YT tutorial
    # new_frame = pd.DataFrame(historical_data)
    # fig = go.Figure(data=[go.Candlestick(x=new_frame.index,
    #                                      open=new_frame['Open'], high=new_frame['High'],
    #                                      low=new_frame['Low'], close=new_frame['Close'])])
    # st.plotly_chart(fig)


    # Apparently there was no need for dataframe
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=historical_data.index, y=historical_data['High'],
                              mode='lines',
                              name='High', line=dict(color='green')))
    # fig2.add_trace(go.Scatter(x=historical_data.index, y=historical_data['Low'],
    #                           mode='lines',
    #                           name='20th percentile', line=dict(color='red', dash='dash')))
    # fig2.add_trace(go.Scatter(x=historical_data.index, y=(historical_data['Close'] - historical_data['Open']),
    #                           mode='lines+markers',
    #                           name='20th percentile', line=dict(color='blue', dash='dash')))
    # 'Volume' is not on the same scale.
    # If displayed with the others, the chart is harder to read
    # fig2.add_trace(go.Scatter(x=historical_data.index, y=historical_data['Volume'],
    #                           mode='lines',
    #                           name='20th percentile', line=dict(color='blue', dash='dash')))
    st.plotly_chart(fig2)

    st.write("Volume")

    # @TODO: You can zoom on charts. but the problem is, you do not control how you can zoom.
    # Which sometimes makes the charts harder to read. We should at least try to do something about it.
    volume_chart = go.Figure()
    volume_chart.add_trace(go.Scatter(x=historical_data.index, y=historical_data['Volume'],
                              mode='lines',
                              name='Voume', line=dict(color='blue')))
    st.plotly_chart(volume_chart)

    # Fetch basic financials
    financials = ticker.financials
    st.write("\nFinancials:")
    st.write(financials)

    # Fetch stock actions like dividends and splits
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
    st.write(f"Selected: {selected_value.get("Symbol")} | {selected_value.get("Short name")}")
    get_financial_data(selected_value.get("Symbol"))



### Very simple search bar
# ticker = st.text_input("First name")
# st.write(ticker)

### How to search for a ticker with yf
# tickers = yf.Search("AA", max_results=10).quotes
# print(tickers)

###

# Roadmap

# Step 1: Get a ticker and display data about it
# @TODO List:
# Take care of suggestions when searching for a symbol / ticker
### Searchbar:

###