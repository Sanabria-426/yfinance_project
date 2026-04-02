import streamlit as st
import yfinance as yf
import pandas as pd

from streamlit_searchbox import st_searchbox

def search_function(searchterm: str):
    if not searchterm:
        return []
    tickers = yf.Search(searchterm, max_results=10).quotes
    # @TODO: Styling for the elements in the searchbar
    # @TODO: Workaround to display nicely and return efficiently
    # Thought: Maybe parse the string once received. I need only the symbol after all

    return [
        {"Symbol": i['symbol'], "Short name": i['shortname']}
    for i in tickers ]

# @TODO: Maybe provide a sidebar for the user to clearly identify what is displayed
def get_financial_data(symbol: str):
    # Create a Ticker object
    ticker = yf.Ticker(symbol)

    # Fetch historical market data for the last year
    # @TODO: Let the user choose the time period

    historical_data = ticker.history(period="1y")

    # Display a summary of the fetched data
    st.write("Historical Data:")
    st.write(historical_data[['Open', 'High', 'Low', 'Close', 'Volume']])

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
    st.write(f"Selected: {selected_value["Symbol"]} | {selected_value["Short name"]}")
    get_financial_data(selected_value["Symbol"])



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