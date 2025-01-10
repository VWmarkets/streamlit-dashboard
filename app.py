import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from textblob import TextBlob

# Title
st.title("Comprehensive Financial Dashboard")
st.write("Track your portfolio, options, market news, and Twitter feeds in real time.")

# Sidebar Input
st.sidebar.header("User Input")
tickers = st.sidebar.text_input("Enter stock tickers (comma-separated):", "AAPL, TSLA, NVDA, XOM").split(",")
portfolio_data = st.sidebar.text_area("Enter portfolio (Ticker, Quantity, Price):", "AAPL, 10, 150\nTSLA, 5, 700")

# Fetch Stock Data
@st.cache_data
def fetch_data(ticker_list):
    data = {}
    for ticker in ticker_list:
        try:
            df = yf.download(ticker.strip(), period="1y", interval="1d")
            df['SMA_50'] = df['Close'].rolling(window=50).mean()
            df['SMA_200'] = df['Close'].rolling(window=200).mean()
            df['RSI'] = calculate_rsi(df['Close'])
            data[ticker.strip()] = df
        except Exception as e:
            st.warning(f"Error fetching data for {ticker.strip()}: {e}")
    return data

# Calculate RSI
def calculate_rsi(series, window=14):
    delta = series.diff(1)
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=window, min_periods=1).mean()
    avg_loss = loss.rolling(window=window, min_periods=1).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# Estimate True Value
def estimate_true_value(df):
    try:
        pe_ratio = 20  # Assume a standard P/E ratio
        growth_rate = 1.1  # Assume a 10% growth rate
        sma_50 = df['SMA_50'][-1]
        true_value = sma_50 * growth_rate if not np.isnan(sma_50) else np.nan
        return true_value
    except Exception as e:
        return np.nan

# Fetch data
data = fetch_data(tickers)

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["Portfolio Overview", "RSI Alerts", "News & Indicators", "Twitter Feeds"])

# Tab 1: Portfolio Overview
with tab1:
    st.subheader("Portfolio Overview")
    portfolio = [row.split(",") for row in portfolio_data.split("\n") if row.strip()]
    for ticker, qty, price in portfolio:
        qty, price = int(qty.strip()), float(price.strip())
        if ticker.strip() in data:
            df = data[ticker.strip()]
            st.write(f"**{ticker.strip()}**")
            st.line_chart(df[['Close', 'SMA_50', 'SMA_200']])
            true_value = estimate_true_value(df)
            st.write(f"Estimated True Value: **${true_value:.2f}**")
        else:
            st.warning(f"No data for {ticker.strip()}")

# Tab 2: RSI Alerts
with tab2:
    st.subheader("RSI Alerts")
    for ticker, df in data.items():
        if 'RSI' in df.columns:
            st.write(f"**{ticker} RSI**")
            st.line_chart(df['RSI'])
        else:
            st.warning(f"No RSI data for {ticker}")

# Tab 3: News & Indicators
with tab3:
    st.subheader("News & Indicators")
    st.write("Coming soon...")

# Tab 4: Twitter Feeds
with tab4:
    st.subheader("Twitter Feeds")
    st.write("Coming soon...")
