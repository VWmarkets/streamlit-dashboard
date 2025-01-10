import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import tweepy
import warnings

# Suppress syntax warnings
warnings.filterwarnings("ignore", category=SyntaxWarning)

# Twitter API credentials
API_KEY = "JUg3iosEqSQmoIhYZ0v7L00lb"
API_SECRET = "o5lMD5hZPisDUAQWeNjylcTZhAiLTaUk5vlpjnHsArGx63wJPv"
ACCESS_TOKEN = "223349059-GXgu6GxgLVGjslDmUxD9ZWBfAI8cgcyt4DHLp3fe"
ACCESS_TOKEN_SECRET = "Bz0LIDjjdD8fEcrNAsFkWpozCqjw6GsY8Djr6LOzAr0LJ"

# Authenticate with Twitter API
auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

# Title
st.title("Comprehensive Financial Dashboard")
st.write("Track your portfolio, options, market news, and Twitter feeds in real time.")

# Sidebar User Input
st.sidebar.header("User Input")
tickers = st.sidebar.text_input("Enter stock tickers (comma-separated):", "AAPL, TSLA, NVDA, XOM")
portfolio_data = st.sidebar.text_area("Enter portfolio (Ticker, Quantity, Price):", "AAPL, 10, 150\nTSLA, 5, 700")

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Portfolio Overview", "RSI Alerts", "Options Analysis", "News & Indicators", "Twitter Feeds"])

# Fetch stock data
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
            st.error(f"Error fetching data for {ticker}: {e}")
    return data

ticker_list = [ticker.strip() for ticker in tickers.split(",")]
stock_data = fetch_data(ticker_list)

# Portfolio Overview Tab
with tab1:
    st.header("Portfolio Overview")
    for ticker in ticker_list:
        if ticker in stock_data:
            st.subheader(ticker)
            df = stock_data[ticker]
            try:
                st.line_chart(df[['Close', 'SMA_50', 'SMA_200']])
            except Exception as e:
                st.warning(f"Error plotting data for {ticker}: {e}")

    # Portfolio calculation
    total_value = 0
    if portfolio_data:
        portfolio_rows = [row.split(",") for row in portfolio_data.split("\n")]
        for row in portfolio_rows:
            try:
                ticker, quantity, price = row[0].strip(), int(row[1]), float(row[2])
                if ticker in stock_data:
                    current_price = stock_data[ticker]['Close'][-1]
                    total_value += quantity * current_price
            except Exception as e:
                st.error(f"Error processing portfolio row {row}: {e}")
    st.write(f"**Total Portfolio Value:** ${total_value:,.2f}")

# RSI Alerts Tab
with tab2:
    st.header("RSI Alerts")
    for ticker in ticker_list:
        if ticker in stock_data:
            df = stock_data[ticker]
            df['RSI'] = 100 - (100 / (1 + df['Close'].diff().clip(lower=0).rolling(14).mean() / df['Close'].diff().clip(upper=0).abs().rolling(14).mean()))
            st.subheader(ticker)
            st.line_chart(df['RSI'])
            latest_rsi = df['RSI'].iloc[-1]
            if latest_rsi > 70:
                st.warning(f"{ticker} is overbought with an RSI of {latest_rsi:.2f}")
            elif latest_rsi < 30:
                st.success(f"{ticker} is oversold with an RSI of {latest_rsi:.2f}")

# Options Analysis Tab
with tab3:
    st.header("Options Analysis")
    st.write("Options analysis will be implemented soon!")

# News & Indicators Tab
with tab4:
    st.header("News & Indicators")
    st.write("Economic news and market indicators will be added soon!")

# Twitter Feeds Tab
with tab5:
    st.header("Twitter Feeds")
    usernames = st.text_input("Enter Twitter usernames (comma-separated):", "elonmusk, realDonaldTrump")
    for username in usernames.split(","):
        try:
            tweets = api.user_timeline(screen_name=username.strip(), count=5)
            st.subheader(f"@{username.strip()}")
            for tweet in tweets:
                st.write(tweet.text)
        except Exception as e:
            st.error(f"Error fetching tweets for {username.strip()}: {e}")
