import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import datetime import matplotlib.pyplot as plt

st.set_page_config(layout="wide") st.title("📈 Krushna's K-Zone Scalper (Supply & Demand Zone Detector)")

--- Sidebar Options ---

symbol = st.sidebar.selectbox("Select Symbol", ["^NSEI", "^NSEBANK"], index=0) timeframe = st.sidebar.selectbox("Select Timeframe", ["1m", "5m"], index=0) lookback_minutes = st.sidebar.slider("Lookback (minutes)", 30, 240, 90)

--- Download Data ---

interval_map = {"1m": "1m", "5m": "5m"} period_map = {"1m": "1d", "5m": "5d"}

data = yf.download(tickers=symbol, period=period_map[timeframe], interval=interval_map[timeframe]) data.dropna(inplace=True) data = data[-lookback_minutes:]  # Trim to lookback window

--- Zone Detection ---

def detect_zones(df, lookback=10, threshold=0.4): supply = [] demand = [] for i in range(lookback, len(df) - lookback): high = df['High'][i] low = df['Low'][i] base_vol = df['Volume'][i-lookback:i+lookback].mean()

# Supply Zone
    if high == max(df['High'][i-lookback:i+lookback]):
        fall = (high - min(df['Low'][i+1:i+lookback])) / high * 100
        if fall > threshold:
            vol_score = df['Volume'][i] / base_vol
            score = int(fall * 30 + vol_score * 20)
            supply.append((df.index[i], high, score))

    # Demand Zone
    if low == min(df['Low'][i-lookback:i+lookback]):
        rise = (max(df['High'][i+1:i+lookback]) - low) / low * 100
        if rise > threshold:
            vol_score = df['Volume'][i] / base_vol
            score = int(rise * 30 + vol_score * 20)
            demand.append((df.index[i], low, score))
return supply, demand

supply_zones, demand_zones = detect_zones(data)

--- Plotting ---

fig, ax = plt.subplots(figsize=(14, 6)) ax.plot(data.index, data['Close'], label='Close Price', color='black')

for t, price, score in supply_zones: ax.axhline(price, color='red', linestyle='--', alpha=0.5) ax.text(data.index[-1], price, f"S:{score}", color='red', va='bottom')

for t, price, score in demand_zones: ax.axhline(price, color='green', linestyle='--', alpha=0.5) ax.text(data.index[-1], price, f"D:{score}", color='green', va='top')

ax.set_title(f"{symbol} | {timeframe} | Supply & Demand Zones") ax.set_ylabel("Price") ax.legend() ax.grid() st.pyplot(fig)

--- Alerts Section ---

st.subheader("📢 Trade Alerts") latest_price = data['Close'].iloc[-1] alerts = []

for t, price, score in demand_zones: if abs(latest_price - price) < 0.2: alerts.append(f"🟩 Demand Zone Hit @ {price:.2f} | Score: {score}")

for t, price, score in supply_zones: if abs(latest_price - price) < 0.2: alerts.append(f"🟥 Supply Zone Hit @ {price:.2f} | Score: {score}")

if alerts: for alert in alerts: st.success(alert) else: st.info("No active alerts. Waiting for price to enter a zone...")

