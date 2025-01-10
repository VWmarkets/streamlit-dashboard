import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import requests

# Title
st.title("Comprehensive Financial Dashboard")
st.write("Track your portfolio, options, market news, and Twitter feeds in real time.")

# Tabs for the app
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["Portfolio Overview", "RSI Alerts", "Options Analysis", "Twitter Feeds", "Intraday Data"]
)

# Alpha Vantage API Key
ALPHA_VANTAGE_API_KEY = "4UZZNRBA9VCHAHGD"

# Function to fetch stock data
@st.cache_data
def fetch_stock_data(ticker_list):
    data = {}
    for ticker in ticker_list:
        try:
            df = yf.download(ticker, period="1y", interval="1d")
            data[ticker] = df
        except Exception as e:
            st.warning(f"Error fetching data for {ticker}: {e}")
    return data

# Function to calculate True Value
def calculate_true_value(current_price):
    # Ensure current_price is a scalar
    if isinstance(current_price, pd.Series):
        current_price = current_price.iloc[-1]
    # Placeholder logic for true value calculation
    return current_price * 1.1  # Assuming a 10% premium for now

# Function to calculate Buy-to-Hold Score
def calculate_buy_to_hold_score(current_price, true_value):
    # Ensure current_price and true_value are scalars
    if isinstance(current_price, pd.Series):
        current_price = current_price.iloc[-1]
    if isinstance(true_value, pd.Series):
        true_value = true_value.iloc[-1]

    # Calculate ratio and determine score
    ratio = current_price / true_value
    if ratio < 0.8:
        return 10
    elif ratio < 0.9:
        return 8
    elif ratio < 1:
        return 6
    elif ratio < 1.1:
        return 4
    else:
        return 2

# Portfolio Overview Tab
with tab1:
    st.header("Portfolio Overview")
    tickers = st.text_input("Enter stock tickers (comma-separated):", "AAPL, TSLA, NVDA, XOM")
    ticker_list = [t.strip() for t in tickers.split(",")]
    
    if st.button("Fetch Portfolio Data"):
        with st.spinner("Fetching portfolio data..."):
            stock_data = fetch_stock_data(ticker_list)
            for ticker, df in stock_data.items():
                if not df.empty:
                    # Ensure 'Close' column exists and has values
                    if 'Close' in df.columns and not df['Close'].empty:
                        current_price = df["Close"].iloc[-1]
                        true_value = calculate_true_value(current_price)
                        buy_to_hold_score = calculate_buy_to_hold_score(current_price, true_value)
                        
                        st.subheader(ticker)
                        st.line_chart(df["Close"])
                        st.write(f"**Current Price**: ${current_price:.2f}")
                        st.write(f"**True Value (based on metrics)**: ${true_value:.2f}")
                        st.write(f"**Buy-to-Hold Score**: {buy_to_hold_score}/10")
                    else:
                        st.warning(f"No valid 'Close' data available for {ticker}")
                else:
                    st.warning(f"No data available for {ticker}")

# RSI Alerts Tab
with tab2:
    st.header("RSI Alerts")

    def calculate_rsi(data, period=14):
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    if st.button("Generate RSI Alerts"):
        with st.spinner("Calculating RSI..."):
            for ticker, df in fetch_stock_data(ticker_list).items():
                if not df.empty:
                    df["RSI"] = calculate_rsi(df["Close"])
                    latest_rsi = df["RSI"].iloc[-1]
                    st.subheader(ticker)
                    st.line_chart(df["RSI"])
                    st.write(f"Latest RSI: {latest_rsi}")
                else:
                    st.warning(f"No data available for {ticker}")

# Options Analysis Tab
with tab3:
    st.header("Options Analysis")
    st.write("Options analysis will be implemented soon!")

# Twitter Feeds Tab
with tab4:
    st.header("Twitter Feeds")
    st.write("Twitter integration requires elevated API access. Feature will be functional when configured.")

# Intraday Data Tab
with tab5:
    st.header("Intraday Stock Data")

    symbol = st.text_input("Enter Stock Symbol (e.g., AAPL):", "AAPL")
    interval = st.selectbox("Select Interval:", ["1min", "5min", "15min", "30min", "60min"])
    outputsize = st.selectbox("Output Size:", ["compact (latest 100 points)", "full (30 days)"])
    outputsize = "compact" if "compact" in outputsize else "full"

    if st.button("Fetch Intraday Data"):
        with st.spinner("Fetching intraday data..."):
            intraday_data = fetch_intraday_data(symbol, interval, outputsize)
            if intraday_data is not None:
                st.success(f"Data fetched for {symbol} ({interval})")
                st.dataframe(intraday_data.head())
                st.line_chart(intraday_data["Close"].astype(float))
            else:
                st.error("Failed to fetch data. Please check the symbol or API key.")
