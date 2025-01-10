import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import requests
from textblob import TextBlob

# Set API keys
NEWS_API_KEY = "YOUR_NEWSAPI_KEY"

# Title and Tabs
st.title("Comprehensive Financial Dashboard")
st.write("Track your portfolio, options, market news, and Twitter feeds in real time.")
tabs = st.tabs(["Portfolio Overview", "RSI Alerts", "Options Analysis", "News & Indicators"])

# Sidebar Inputs
st.sidebar.header("User Input")
tickers = st.sidebar.text_input("Enter stock tickers (comma-separated):", "AAPL, TSLA, NVDA, XOM")
portfolio_data = st.sidebar.text_area("Enter portfolio (Ticker, Quantity, Price):", "AAPL, 10, 150\nTSLA, 5, 700")

# Split tickers
ticker_list = [t.strip().upper() for t in tickers.split(",")]

# Portfolio Data Parsing
portfolio = []
for line in portfolio_data.split("\n"):
    try:
        symbol, qty, price = line.split(",")
        portfolio.append({"Ticker": symbol.strip().upper(), "Quantity": int(qty.strip()), "Price": float(price.strip())})
    except:
        continue

# Tab: Portfolio Overview
with tabs[0]:
    st.subheader("Portfolio Overview")
    portfolio_df = pd.DataFrame(portfolio)
    if not portfolio_df.empty:
        portfolio_value = 0
        for ticker in portfolio_df["Ticker"]:
            try:
                data = yf.Ticker(ticker).history(period="1d")
                current_price = data["Close"].iloc[-1]
                portfolio_df.loc[portfolio_df["Ticker"] == ticker, "Current Price"] = current_price
                portfolio_df.loc[portfolio_df["Ticker"] == ticker, "Value"] = (
                    portfolio_df.loc[portfolio_df["Ticker"] == ticker, "Quantity"] * current_price
                )
                portfolio_value += portfolio_df.loc[portfolio_df["Ticker"] == ticker, "Value"].values[0]
            except Exception as e:
                st.warning(f"Error fetching data for {ticker}: {e}")
        st.write(portfolio_df)
        st.write(f"**Total Portfolio Value: ${portfolio_value:,.2f}**")
    else:
        st.warning("No portfolio data provided.")

# Tab: RSI Alerts
with tabs[1]:
    st.subheader("RSI Alerts")
    for ticker in ticker_list:
        try:
            data = yf.download(ticker, period="6mo", interval="1d")
            data["RSI"] = 100 - (100 / (1 + data["Close"].diff().apply(lambda x: x if x > 0 else 0).mean() / data["Close"].diff().apply(lambda x: -x if x < 0 else 0).mean()))
            st.write(f"{ticker} RSI")
            st.line_chart(data["RSI"])
        except Exception as e:
            st.warning(f"Error calculating RSI for {ticker}: {e}")

# Tab: Options Analysis
with tabs[2]:
    st.subheader("Options Analysis")
    for ticker in ticker_list:
        try:
            stock = yf.Ticker(ticker)
            options = stock.option_chain(stock.options[0])
            st.write(f"Options Chain for {ticker} (Expiration: {stock.options[0]})")
            st.write("Calls:")
            st.write(options.calls)
            st.write("Puts:")
            st.write(options.puts)
        except Exception as e:
            st.warning(f"Error fetching options for {ticker}: {e}")

# Tab: News & Indicators
with tabs[3]:
    st.subheader("News & Indicators")
    for ticker in ticker_list:
        try:
            url = f"https://newsapi.org/v2/everything?q={ticker}&apiKey={NEWS_API_KEY}"
            response = requests.get(url)
            articles = response.json().get("articles", [])
            if articles:
                st.write(f"News for {ticker}")
                for article in articles[:5]:
                    sentiment = TextBlob(article["title"]).sentiment.polarity
                    sentiment_text = "Positive" if sentiment > 0 else "Negative" if sentiment < 0 else "Neutral"
                    st.write(f"- [{article['title']}]({article['url']}) ({sentiment_text})")
            else:
                st.warning(f"No news found for {ticker}.")
        except Exception as e:
            st.warning(f"Error fetching news for {ticker}: {e}")
