import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt

# Page settings
st.set_page_config(page_title="KZone Scalper", layout="wide")
st.title("📊 KZone Supply & Demand Zone Scanner")

# User inputs
ticker = st.selectbox("Select Stock Symbol", ["RELIANCE.BO", "INFY.BO", "TCS.BO", "HDFCBANK.BO"])
timeframe = st.selectbox("Timeframe", ["1m", "5m"])
days = st.slider("Number of Days to Fetch", 1, 10, 3)

# Fetch data from Yahoo Finance
def fetch_data(symbol, interval, days):
    end = datetime.datetime.now()
    start = end - datetime.timedelta(days=days)
    df = yf.download(symbol, interval=interval, start=start, end=end, progress=False)
    df.dropna(inplace=True)
    return df

# Supply and Demand Zone Detection
def detect_zones(df):
    zones = []
    for i in range(2, len(df) - 2):
        low = df['Low'].iloc[i]
        high = df['High'].iloc[i]

        if low < df['Low'].iloc[i - 1] and low < df['Low'].iloc[i - 2] and \
           low < df['Low'].iloc[i + 1] and low < df['Low'].iloc[i + 2]:
            zones.append((df.index[i], low, 'Demand'))

        if high > df['High'].iloc[i - 1] and high > df['High'].iloc[i - 2] and \
           high > df['High'].iloc[i + 1] and high > df['High'].iloc[i + 2]:
            zones.append((df.index[i], high, 'Supply'))
    return zones

# Main logic
data = fetch_data(ticker, timeframe, days)
zones = detect_zones(data)

# Plotting
fig, ax = plt.subplots(figsize=(14, 6))
ax.plot(data.index, data['Close'], label='Close Price', color='blue')

for time, price, ztype in zones:
    color = 'green' if ztype == 'Demand' else 'red'
    ax.axhline(y=price, color=color, linestyle='--', linewidth=1.2)
    ax.text(data.index[-1], price, f"{ztype} @ {price:.2f}", color=color, va='bottom', fontsize=9)

ax.set_title(f"{ticker} | Timeframe: {timeframe}")
ax.set_xlabel("Time")
ax.set_ylabel("Price")
ax.legend()
fig.autofmt_xdate()
st.pyplot(fig)

# Show data table
with st.expander("📋 Show Raw OHLC Data"):
    st.dataframe(data.tail(50))
