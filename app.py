import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

# Title
st.title("Comprehensive Financial Dashboard")
st.write("Track your portfolio, options, and market news in real time.")

# Sidebar: User Input
st.sidebar.header("User Input")
tickers = st.sidebar.text_input("Enter stock tickers (comma-separated):", "AAPL, TSLA, NVDA, XOM")
portfolio_data = st.sidebar.text_area("Enter portfolio (Ticker, Quantity, Price):", "AAPL, 10, 150\nTSLA, 5, 700")

# Fetch Stock Data
@st.cache_data
def fetch_data(ticker_list):
    data = {}
    for ticker in ticker_list:
        data[ticker] = yf.download(ticker, period="1y", interval="1d")
    return data

# Calculate Moving Averages
def add_moving_averages(data, window=50):
    data[f"SMA_{window}"] = data['Close'].rolling(window).mean()
    return data

ticker_list = [ticker.strip() for ticker in tickers.split(",")]
stock_data = fetch_data(ticker_list)

# Portfolio Overview Tab
tab1, tab2, tab3, tab4 = st.tabs(["Portfolio Overview", "RSI Alerts", "Options Analysis", "News & Indicators"])

# Tab 1: Portfolio Overview
with tab1:
    st.subheader("Portfolio Overview")
    total_value = 0
    for ticker in ticker_list:
        st.write(f"### {ticker}")
        data = stock_data[ticker]
        data = add_moving_averages(data, window=50)
        data = add_moving_averages(data, window=200)
        st.line_chart(data[['Close', 'SMA_50', 'SMA_200']])
    st.write(f"Total Portfolio Value: ${total_value:.2f}")

# RSI Alerts Tab
with tab2:
    st.subheader("RSI Alerts")
    def calculate_rsi(data, period=14):
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

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

# Options Analysis Tab
with tab3:
    st.subheader("Options Analysis")
    selected_ticker = st.selectbox("Select a stock for options data:", ticker_list)
    options = yf.Ticker(selected_ticker).option_chain()
    st.write(f"**Calls for {selected_ticker}:**")
    st.dataframe(options.calls)
    st.write(f"**Puts for {selected_ticker}:**")
    st.dataframe(options.puts)

# News and Indicators Tab
with tab4:
    st.subheader("News and Indicators")
    st.write("This section will feature real-time news and economic indicators.")
    st.write("Coming soon: Federal Reserve updates, CPI, and more.")

# Footer
st.write("**Note:** This dashboard is for informational purposes only. Please consult a financial advisor.")
