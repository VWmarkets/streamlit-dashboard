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
            df['SMA_50'] = df['Close'].rolling(window=50).mean()
            df['SMA_200'] = df['Close'].rolling(window=200).mean()
            data[ticker] = df
        except Exception as e:
            st.warning(f"Error fetching data for {ticker}: {e}")
    return data

# Function to calculate true value
def calculate_true_value(df):
    if 'Close' in df.columns and 'SMA_50' in df.columns and 'SMA_200' in df.columns:
        current_price = df['Close'].iloc[-1]
        sma_50 = df['SMA_50'].iloc[-1]
        sma_200 = df['SMA_200'].iloc[-1]
        true_value = (current_price + sma_50 + sma_200) / 3  # Simple weighted average
        return true_value
    return None

# Function to calculate Buy-to-Hold scale
def calculate_buy_to_hold_score(df):
    if 'Close' in df.columns and 'SMA_50' in df.columns and 'RSI' in df.columns:
        current_price = df['Close'].iloc[-1]
        sma_50 = df['SMA_50'].iloc[-1]
        rsi = df['RSI'].iloc[-1]
        
        # Buy-to-Hold Logic
        score = 10
        if current_price > sma_50:
            score -= 2
        if rsi > 70:
            score -= 3  # Penalize overbought RSI
        elif rsi < 30:
            score += 3  # Reward oversold RSI
        return max(1, min(score, 10))  # Ensure score is between 1 and 10
    return None

# Portfolio Overview Tab
with tab1:
    st.header("Portfolio Overview")
    tickers = st.text_input("Enter stock tickers (comma-separated):", "AAPL, TSLA, NVDA, XOM")
    ticker_list = [t.strip() for t in tickers.split(",")]
    
    if st.button("Fetch Portfolio Data"):
        with st.spinner("Fetching portfolio data..."):
            stock_data = fetch_stock_data(ticker_list)
            for ticker, df in stock_data.items():
                if not df.empty and 'Close' in df.columns:
                    df['RSI'] = 100 - (100 / (1 + df['Close'].diff().clip(lower=0).rolling(14).mean() /
                                              df['Close'].diff().clip(upper=0).abs().rolling(14).mean()))
                    true_value = calculate_true_value(df)
                    buy_to_hold_score = calculate_buy_to_hold_score(df)
                    
                    st.subheader(ticker)
                    st.line_chart(df[['Close', 'SMA_50', 'SMA_200']])
                    if true_value:
                        st.write(f"**True Value:** ${true_value:.2f}")
                    if buy_to_hold_score:
                        st.write(f"**Buy-to-Hold Score:** {buy_to_hold_score}/10")
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
    usernames = st.text_input("Enter Twitter usernames (comma-separated):", "elonmusk, realDonaldTrump")
    username_list = [u.strip() for u in usernames.split(",")]

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
            base_url = "https://www.alphavantage.co/query"
            params = {
                "function": "TIME_SERIES_INTRADAY",
                "symbol": symbol,
                "interval": interval,
                "outputsize": outputsize,
                "datatype": "json",
                "apikey": ALPHA_VANTAGE_API_KEY,
            }
            response = requests.get(base_url, params=params)
            data = response.json()

            if f"Time Series ({interval})" in data:
                time_series_key = f"Time Series ({interval})"
                intraday_data = data[time_series_key]
                df = pd.DataFrame.from_dict(intraday_data, orient="index")
                df = df.rename(
                    columns={
                        "1. open": "Open",
                        "2. high": "High",
                        "3. low": "Low",
                        "4. close": "Close",
                        "5. volume": "Volume",
                    }
                )
                df.index = pd.to_datetime(df.index)
                df = df.sort_index()
                st.success(f"Data fetched for {symbol} ({interval})")
                st.dataframe(df.head())
                st.line_chart(df["Close"].astype(float))
            else:
                st.error("Failed to fetch data. Please check the symbol or API key.")
