import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from textblob import TextBlob

# Title
st.title("Comprehensive Financial Dashboard")
st.write("Track your portfolio, options, market news, and Twitter feeds in real time.")

# Sidebar: User Input
st.sidebar.header("User Input")
tickers = st.sidebar.text_input(
    "Enter stock tickers (comma-separated):", "AAPL, TSLA, NVDA, XOM"
)
portfolio_data = st.sidebar.text_area(
    "Enter portfolio (Ticker, Quantity, Price):", "AAPL, 10, 150\nTSLA, 5, 700"
)

# Fetch Stock Data
@st.cache_data
def fetch_data(ticker_list):
    data = {}
    for ticker in ticker_list:
        try:
            df = yf.download(ticker, period="1y", interval="1d")
            df['SMA_50'] = df['Close'].rolling(window=50).mean()
            df['SMA_200'] = df['Close'].rolling(window=200).mean()
            data[ticker] = df
        except Exception as e:
            st.warning(f"Could not fetch data for {ticker}: {e}")
    return data


# Function to calculate estimated true value
def estimate_true_value(df):
    if 'Close' in df.columns:
        recent_close = df['Close'].iloc[-1]
        sma_50 = df['SMA_50'].iloc[-1] if 'SMA_50' in df.columns else np.nan
        sma_200 = df['SMA_200'].iloc[-1] if 'SMA_200' in df.columns else np.nan
        return (recent_close + sma_50 + sma_200) / 3
    return np.nan


# Fetch Data
ticker_list = [ticker.strip() for ticker in tickers.split(",")]
data = fetch_data(ticker_list)

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
            # Check for necessary columns
            if all(col in df.columns for col in ['Close', 'SMA_50', 'SMA_200']):
                st.line_chart(df[['Close', 'SMA_50', 'SMA_200']])
                true_value = estimate_true_value(df)
                st.write(f"Estimated True Value: **${true_value:.2f}**")
            else:
                missing_cols = [col for col in ['Close', 'SMA_50', 'SMA_200'] if col not in df.columns]
                st.warning(f"Missing data for {ticker.strip()}: {', '.join(missing_cols)}")
        else:
            st.warning(f"No data for {ticker.strip()}")

# Tab 2: RSI Alerts
with tab2:
    st.subheader("RSI Alerts")
    def calculate_rsi(df, window=14):
        delta = df['Close'].diff()
        gain = np.where(delta > 0, delta, 0)
        loss = np.where(delta < 0, -delta, 0)
        avg_gain = pd.Series(gain).rolling(window=window).mean()
        avg_loss = pd.Series(loss).rolling(window=window).mean()
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    for ticker in ticker_list:
        if ticker in data:
            df = data[ticker]
            if 'Close' in df.columns:
                df['RSI'] = calculate_rsi(df)
                st.write(f"**{ticker} RSI**")
                st.line_chart(df['RSI'])
            else:
                st.warning(f"No Close data for {ticker} to calculate RSI.")

# Tab 3: News & Indicators
with tab3:
    st.subheader("News & Indicators")
    st.write("News and economic indicators will be added soon!")

# Tab 4: Twitter Feeds
with tab4:
    st.subheader("Twitter Feeds")
    twitter_users = st.text_input("Enter Twitter usernames (comma-separated):", "elonmusk, realDonaldTrump")
    st.warning("Twitter integration is currently unavailable.")
