import yfinance as yf

# Define the ticker symbol
ticker_symbol = "AAPL"
ticker = yf.Ticker(ticker_symbol)
#
# only_stock = yf.Lookup("AAP").get_stock(count=50)
#
# print(only_stock["shortName"])

calendars = yf.Calendars()
earnings_calendar = calendars.get_earnings_calendar(limit=50)
print(earnings_calendar)

# # Fetch historical market data for the last year
# historical_data = ticker.history(period="1y")
# print(historical_data)
#
# # Fetch basic financials (income statement, balance sheet, cash flow)
# financials = ticker.financials
# print("\nFinancials:")
# print(financials)
#
# # Fetch stock actions like dividends and splits
# actions = ticker.actions
# print("\nStock Actions:")
# print(actions)
#
# # Get general stock information
# info = ticker.info
# print("\nStock Information:")
# print(info)