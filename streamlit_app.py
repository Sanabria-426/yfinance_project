
### @What to do next?
# Allow to decide of the interval
#

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
    # @TODO: Error when no result - check on that - That might be because the value for symbols was retrieved without get
    # @TODO: Check if the numbers (millions) could be more readable

    return [
        {"Symbol": i.get('symbol'), "Short name": i.get('shortname')}
    for i in tickers ]

def get_financial_data(symbol: str):

    ticker = yf.Ticker(symbol)

    with historical_data_tab:

        start_date, end_date = date_range_picker(
            "Select a range for the historical data",
            default_start=date.today() - timedelta(days=30),
            default_end=date.today(),
            min_date=date(1970, 1, 1),
            max_date=date.today(),
            error_message="Please select start and end date"
        )

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

        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=historical_data.index, y=historical_data['High'],
                                  mode='lines',
                                  name='High', line=dict(color='green')))
        st.plotly_chart(fig2)

        st.write("Volume")

        # @TODO: You can zoom on charts. but the problem is, you do not control how you can zoom.
        # Which sometimes makes the charts harder to read. We should at least try to do something about it.
        volume_chart = go.Figure()
        volume_chart.add_trace(go.Scatter(x=historical_data.index, y=historical_data['Volume'],
                                  mode='lines',
                                  name='Volume', line=dict(color='blue')))
        st.plotly_chart(volume_chart)

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
    st.write(f"Selected: {selected_value.get("Symbol")} | {selected_value.get("Short name")}")

    historical_data_tab, financials_tab, stock_actions_tab = st.tabs(["Historical Data", "Financials", "Stock Actions"])

    get_financial_data(selected_value.get("Symbol"))
