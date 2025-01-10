import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import requests
from textblob import TextBlob

# Title
st.title("Comprehensive Financial Dashboard")
st.write("Track your portfolio, options, market news, and Twitter feeds in real time.")

# API Keys
ALPHA_VANTAGE_API_KEY = "4UZZNRBA9VCHAHGD"
POLYGON_API_KEY = "xRygUS5Dq37UzkKuHtjnCHmFocKp7yVA"

# Tabs for the app
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["Portfolio Overview", "RSI Alerts", "Options Analysis", "Twitter Feeds", "Intraday Data"]
)

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
                    current_price = float(df["Close"].iloc[-1]) if not df["Close"].empty else 0.0
                    st.subheader(f"{ticker}")
                    st.line_chart(df["Close"])
                    st.write(f"**Current Price**: ${current_price:.2f}")
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
    st.header("Top 5 Options Plays")

    # User inputs
    ticker = st.text_input("Enter Stock Ticker (e.g., AAPL):", "AAPL")
    expiry_date = st.text_input("Enter Expiration Date (YYYY-MM-DD):", "")
    risk_level = st.selectbox("Select Risk Level:", ["Conservative", "Moderate", "Aggressive"])

    # Polygon API endpoint
    def fetch_options_data(ticker):
        """Fetch options data for a given ticker."""
        url = f"https://api.polygon.io/v3/snapshot/options/{ticker}?apiKey={POLYGON_API_KEY}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error fetching options data: {response.status_code}")
            return None

    # Analyze Options Data
    def analyze_options(data, risk_level):
        """Filter and rank options based on risk level."""
        options = pd.DataFrame(data['results'])

        # Calculate Potential ROI (placeholder logic)
        options['Potential ROI'] = options['implied_volatility'] * 100  # Example formula

        # Filter options based on risk level
        if risk_level == "Conservative":
            filtered = options[options['delta'].abs() < 0.4]
        elif risk_level == "Moderate":
            filtered = options[(options['delta'].abs() >= 0.4) & (options['delta'].abs() <= 0.6)]
        else:
            filtered = options[options['delta'].abs() > 0.6]

        # Sort by ROI and return top 5
        return filtered.nlargest(5, 'Potential ROI')

    # Fetch and Display Options
    if st.button("Fetch Top Options Plays"):
        with st.spinner("Fetching and analyzing options data..."):
            try:
                data = fetch_options_data(ticker)
                if data and 'results' in data:
                    top_options = analyze_options(data, risk_level)
                    st.success(f"Top 5 Options Plays for {ticker}")
                    st.dataframe(top_options[['symbol', 'strike_price', 'expiration_date', 'implied_volatility', 'delta', 'Potential ROI']])
                else:
                    st.error("No options data available. Please check the ticker or API key.")
            except Exception as e:
                st.error(f"Error fetching options data: {e}")

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
