import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import tweepy

# Title
st.title("Comprehensive Financial Dashboard")
st.write("Track your portfolio, options, market news, and Twitter feeds in real time.")

# Sidebar: User Input
st.sidebar.header("User Input")
tickers = st.sidebar.text_input("Enter stock tickers (comma-separated):", "AAPL, TSLA, NVDA, XOM")
portfolio_data = st.sidebar.text_area("Enter portfolio (Ticker, Quantity, Price):", "AAPL, 10, 150\nTSLA, 5, 700")

# Twitter API Credentials
TWITTER_API_KEY = "JUg3iosEqSQmoIhYZ0v7L00lb"
TWITTER_API_SECRET = "o5lMD5hZPisDUAQWeNjylcTZhAiLTaUk5vlpjnHsArGx63wJPv"
TWITTER_BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAGo1yAEAAAAA9vaULLXHOi6dvqjSinc1E0WIYYE%3D6C2xzeBt2Zx4uUxaPGIKWHoJSqVrlq453QAt9TdqDXOXSu7phB"
ACCESS_TOKEN = "223349059-GXgu6GxgLVGjslDmUxD9ZWBfAI8cgcyt4DHLp3fe"
ACCESS_TOKEN_SECRET = "Bz0LIDjjdD8fEcrNAsFkWpozCqjw6GsY8Djr6LOzAr0LJ"

# Twitter Client Setup
@st.cache_resource
def twitter_client():
    client = tweepy.Client(
        bearer_token=TWITTER_BEARER_TOKEN,
        consumer_key=TWITTER_API_KEY,
        consumer_secret=TWITTER_API_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_TOKEN_SECRET,
    )
    return client

client = twitter_client()

# Fetch Tweets Function
def fetch_tweets(username, max_results=5):
    try:
        user = client.get_user(username=username)
        user_id = user.data.id
        tweets = client.get_users_tweets(
            id=user_id, max_results=max_results, tweet_fields=["created_at", "text"]
        )
        return tweets.data if tweets.data else []
    except Exception as e:
        st.warning(f"Error fetching tweets for {username}: {e}")
        return []

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

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Portfolio Overview", "RSI Alerts", "Options Analysis", "News & Indicators", "Twitter Feeds"])

# Tab 5: Twitter Feeds
with tab5:
    st.subheader("Twitter Feeds")
    usernames = st.text_input("Enter Twitter usernames (comma-separated):", "elonmusk, realDonaldTrump")
    username_list = [username.strip() for username in usernames.split(",")]

    for username in username_list:
        st.write(f"### Tweets from @{username}")
        tweets = fetch_tweets(username)
        if tweets:
            for tweet in tweets:
                st.write(f"- **{tweet.created_at}**: {tweet.text}")
        else:
            st.write(f"No tweets found for @{username}.")
