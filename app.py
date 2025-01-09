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
        try:
            data[ticker] = yf.download(ticker, period="1y", interval="1d")
        except Exception as e:
            st.warning(f"Failed to load data for {ticker}: {e}")
    return data

# Calculate Moving Averages with Safeguards
def add_moving_averages(data, window=50):
    if len(data) >= window:
        data[f"SMA_{window}"] = data['Close'].rolling(window).mean()
    else:
        data[f"SMA_{window}"] = np.nan
    return data

# Calculate RSI
def calculate_rsi(data, period=14):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

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
        if ticker not in stock_data or stock_data[ticker].empty:
            st.warning(f"No data available for {ticker}. Skipping...")
            continue

        data = stock_data[ticker]

        # Add moving averages
        data = add_moving_averages(data, window=50)
        data = add_moving_averages(data, window=200)

        # Ensure columns exist before plotting
        columns_to_plot = ['Close']
        for column in ["SMA_50", "SMA_200"]:
            if column in data.columns:
                columns_to_plot.append(column)

        st.line_chart(data[columns_to_plot])

        # Calculate portfolio value
        portfolio_rows = portfolio_data.split("\n")
        for row in portfolio_rows:
            row_data = row.split(",")
            if len(row_data) == 3 and row_data[0].strip() == ticker:
                try:
                    quantity = float(row_data[1].strip())
                    cost_price = float(row_data[2].strip())
                    current_price = data['Close'].iloc[-1]
                    total_value += quantity * current_price
                except Exception:
                    st.warning(f"Could not calculate value for {ticker}. Check portfolio input.")

    st.write(f"Total Portfolio Value: ${total_value:.2f}")

# RSI Alerts Tab
with tab2:
    st.subheader("RSI Alerts")
    for ticker in ticker_list:
        if ticker not in stock_data or stock_data[ticker].empty:
            st.warning(f"No data available for {ticker}. Skipping...")
            continue

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
    if selected_ticker not in stock_data or stock_data[selected_ticker].empty:
        st.warning(f"No data available for {selected_ticker}.")
    else:
        try:
            options = yf.Ticker(selected_ticker).option_chain()
            st.write(f"**Calls for {selected_ticker}:**")
            st.dataframe(options.calls)
            st.write(f"**Puts for {selected_ticker}:**")
            st.dataframe(options.puts)
        except Exception as e:
            st.warning(f"Failed to load options data for {selected_ticker}: {e}")

# News and Indicators Tab
with tab4:
    st.subheader("News and Indicators")
    st.write("This section will feature real-time news and economic indicators.")
    st.write("Coming soon: Federal Reserve updates, CPI, and more.")

# Footer
st.write("**Note:** This dashboard is for informational purposes only. Please consult a financial advisor.")
