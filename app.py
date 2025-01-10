import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import requests
from textblob import TextBlob

# Title
st.title("Ultimate Financial Dashboard - Powered by AI")
st.write("Track your portfolio, market trends, and the best investment opportunities using cutting-edge AI insights.")

# API Keys
ALPHA_VANTAGE_API_KEY = "4UZZNRBA9VCHAHGD"
FMP_API_KEY = "y5BE2TLQBZRMRDAQ1EN4dS4TXBEiSOLQ"
POLYGON_API_KEY = "xRygUS5Dq37UzkKuHtjnCHmFocKp7yVA"

# Tabs for Navigation
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    ["Portfolio Overview", "RSI & Technicals", "Macro Trends", "True Value", "Options Analysis", "Top 5 Picks"]
)

# Utility Functions
@st.cache_data
def fetch_stock_data(ticker):
    return yf.download(ticker, period="1y", interval="1d")

def fetch_polygon_data(symbol, timespan="day", limit=365):
    url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/{timespan}/2022-01-01/2023-01-01?adjusted=true&sort=desc&apiKey={POLYGON_API_KEY}"
    response = requests.get(url)
    return response.json()

def fetch_fmp_data(endpoint, params):
    base_url = f"https://financialmodelingprep.com/api/v3/{endpoint}"
    params["apikey"] = FMP_API_KEY
    response = requests.get(base_url, params=params)
    return response.json()

def calculate_rsi(data, period=14):
    delta = data.diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calculate_true_value(current_price, growth_rate=0.08):
    return current_price * (1 + growth_rate)

def calculate_buy_to_hold_score(current_price, true_value):
    ratio = current_price / true_value
    if ratio < 0.8:
        return 10
    elif ratio < 0.9:
        return 8
    elif ratio < 1.0:
        return 6
    else:
        return 4

# Portfolio Overview
with tab1:
    st.header("Portfolio Overview")
    tickers = st.text_input("Enter stock tickers (comma-separated):", "AAPL, TSLA, NVDA, MSFT")
    ticker_list = [t.strip().upper() for t in tickers.split(",")]

    if st.button("Fetch Data"):
        for ticker in ticker_list:
            df = fetch_stock_data(ticker)
            if not df.empty:
                st.subheader(f"{ticker}")
                st.line_chart(df["Close"])
                st.write(f"Current Price: ${df['Close'].iloc[-1]:.2f}")

# RSI & Technical Indicators
with tab2:
    st.header("RSI & Technical Indicators")
    for ticker in ticker_list:
        df = fetch_stock_data(ticker)
        if not df.empty:
            df["RSI"] = calculate_rsi(df["Close"])
            st.subheader(f"{ticker} RSI")
            st.line_chart(df["RSI"])

# Macro Trends
with tab3:
    st.header("Macro Trends")
    data = fetch_polygon_data("SPY")  # Example: S&P 500 data
    st.write("Market Trends: S&P 500")
    st.write(data)

# True Value Analysis
with tab4:
    st.header("True Value")
    for ticker in ticker_list:
        df = fetch_stock_data(ticker)
        if not df.empty:
            current_price = df["Close"].iloc[-1]
            true_value = calculate_true_value(current_price)
            score = calculate_buy_to_hold_score(current_price, true_value)
            st.subheader(f"{ticker}")
            st.write(f"Current Price: ${current_price:.2f}")
            st.write(f"True Value: ${true_value:.2f}")
            st.write(f"Buy-to-Hold Score: {score}/10")

# Options Analysis
with tab5:
    st.header("Options Analysis")
    st.write("Coming soon: Options screener with top plays!")

# Top 5 Picks
with tab6:
    st.header("Top 5 Picks - Buy/Sell")
    st.write("Coming soon: Combined metrics to rank top stocks to buy/sell!")
