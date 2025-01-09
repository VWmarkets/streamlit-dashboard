import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import requests

# Title
st.title("Comprehensive Financial Dashboard")
st.write("Track your portfolio, options, and market news in real time.")

# Sidebar: User Input
st.sidebar.header("User Input")
tickers = st.sidebar.text_input("Enter stock tickers (comma-separated):", "AAPL, TSLA, NVDA, XOM")
portfolio_data = st.sidebar.text_area("Enter portfolio (Ticker, Quantity, Price):", "AAPL, 10, 150\nTSLA, 5, 700")

# NewsAPI Key
NEWS_API_KEY = "5cd9644b766a41368874c9fcef66b58b"

# Fetch Stock Data
@st.cache_data
def fetch_data(ticker_list):
    data = {}
    for ticker in ticker_list:
        try:
            df = yf.download(ticker, period="1y", interval="1d")
            if 'Close' in df.columns:
                data[ticker] = df
            else:
                st.warning(f"Missing 'Close' data for {ticker}. Skipping...")
        except Exception as e:
            st.warning(f"Failed to load data for {ticker}: {e}")
    return data

# Fetch News Data
@st.cache_data
def fetch_news(ticker):
    url = f"https://newsapi.org/v2/everything?q={ticker}&apiKey={NEWS_API_KEY}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json().get("articles", [])
        else:
            st.warning(f"Failed to fetch news for {ticker}: {response.status_code}")
            return []
    except Exception as e:
        st.warning(f"Error fetching news: {e}")
        return []

# Calculate Moving Averages
def add_moving_averages(data, window):
    if len(data) >= window:
        data[f"SMA_{window}"] = data['Close'].rolling(window).mean()
    return data

# Calculate RSI
def calculate_rsi(data, period=14):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# Prepare Ticker List
ticker_list = [ticker.strip() for ticker in tickers.split(",")]
stock_data = fetch_data(ticker_list)

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["Portfolio Overview", "RSI Alerts", "Options Analysis", "News & Indicators"])

# Tab 1: Portfolio Overview
with tab1:
    st.subheader("Portfolio Overview")
    total_value = 0

    for ticker in ticker_list:
        st.write(f"### {ticker}")

        # Check if data exists for the ticker
        if ticker not in stock_data or stock_data[ticker].empty:
            st.warning(f"No valid data for {ticker}. Skipping...")
            continue

        data = stock_data[ticker]

        # Add moving averages
        try:
            data = add_moving_averages(data, 50)
            data = add_moving_averages(data, 200)

            # Dynamically select available columns for plotting
            available_columns = [col for col in ['Close', 'SMA_50', 'SMA_200'] if col in data.columns]
            if available_columns:
                st.line_chart(data[available_columns])
            else:
                st.warning(f"No valid columns to plot for {ticker}. Skipping chart.")
        except Exception as e:
            st.warning(f"Error processing moving averages for {ticker}: {e}")

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
                except Exception as e:
                    st.warning(f"Could not calculate value for {ticker}: {e}")

    st.write(f"**Total Portfolio Value:** ${total_value:,.2f}")

# Tab 2: RSI Alerts
with tab2:
    st.subheader("RSI Alerts")
    for ticker in ticker_list:
        if ticker not in stock_data or stock_data[ticker].empty:
            st.warning(f"No data available for {ticker}. Skipping...")
            continue

        data = stock_data[ticker]
        try:
            data['RSI'] = calculate_rsi(data)
            recent_rsi = data['RSI'].iloc[-1]
            if recent_rsi < 30:
                st.write(f"**{ticker} is oversold (RSI: {recent_rsi:.2f})**")
            elif recent_rsi > 70:
                st.write(f"**{ticker} is overbought (RSI: {recent_rsi:.2f})**")
            else:
                st.write(f"{ticker} RSI is normal: {recent_rsi:.2f}")
        except Exception as e:
            st.warning(f"Error calculating RSI for {ticker}: {e}")

# Tab 3: Options Analysis
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

# Tab 4: News and Indicators
with tab4:
    st.subheader("News and Indicators")
    st.write("Latest financial news for your selected tickers.")
    for ticker in ticker_list:
        st.write(f"### News for {ticker}")
        articles = fetch_news(ticker)
        if articles:
            for article in articles[:5]:  # Limit to 5 articles per ticker
                st.write(f"- [{article['title']}]({article['url']})")
        else:
            st.write("No news available.")

# Footer
st.write("**Note:** This dashboard is for informational purposes only. Please consult a financial advisor.")
