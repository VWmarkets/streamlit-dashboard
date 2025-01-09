import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

# Title and Description
st.title("Portfolio Dashboard")
st.write("Track your portfolio, market indicators, and trading opportunities in real-time.")

# Sidebar for User Input
st.sidebar.header("User Input")
st.sidebar.write("Add your stocks and track their performance.")
tickers = st.sidebar.text_input("Enter stock tickers (comma-separated):", "AAPL, TSLA, NVDA, XOM")

# Fetch Stock Data
@st.cache_data
def fetch_data(ticker_list):
    data = {}
    for ticker in ticker_list:
        data[ticker] = yf.download(ticker, period="1y", interval="1d")
    return data

ticker_list = [ticker.strip() for ticker in tickers.split(",")]
stock_data = fetch_data(ticker_list)

# Display Stock Data
st.subheader("Portfolio Performance")
for ticker in ticker_list:
    st.write(f"### {ticker}")
    st.line_chart(stock_data[ticker]['Close'])

# RSI Calculation
def calculate_rsi(data, period=14):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# Display RSI Alerts
st.subheader("RSI Alerts")
for ticker in ticker_list:
    data = stock_data[ticker]
    data['RSI'] = calculate_rsi(data)
    recent_rsi = data['RSI'].iloc[-1]
    if recent_rsi < 30:
        st.write(f"**{ticker} is oversold (RSI: {recent_rsi:.2f})**")
    elif recent_rsi > 70:
        st.write(f"**{ticker} is overbought (RSI: {recent_rsi:.2f})**")
    else:
        st.write(f"{ticker} RSI is normal: {recent_rsi:.2f}")

# Options Overview
st.subheader("Options Data")
selected_ticker = st.selectbox("Select a stock for options data:", ticker_list)
options = yf.Ticker(selected_ticker).option_chain()
st.write(f"**Calls for {selected_ticker}:**")
st.dataframe(options.calls)
st.write(f"**Puts for {selected_ticker}:**")
st.dataframe(options.puts)

# Economic Indicators
st.subheader("Economic Indicators")
st.write("Tracking Federal Reserve rates and economic news will be added here.")

# Footer
st.write("**Note:** This dashboard is for informational purposes only. Please consult a financial advisor for professional advice.")
