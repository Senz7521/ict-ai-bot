# =========================================================
# ICT AI BOT ULTRA PRO
# =========================================================

import streamlit as st
from streamlit_autorefresh import st_autorefresh

import ccxt
import pandas as pd
import plotly.graph_objects as go

import requests
import os
import json
import numpy as np

from datetime import datetime

# =========================================================
# AUTO REFRESH
# =========================================================

st_autorefresh(interval=10000, key="refresh")

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="ICT AI BOT ULTRA PRO",
    layout="wide"
)

# =========================================================
# CUSTOM UI
# =========================================================

st.markdown("""
<style>

.stApp {
    background-color: #0e1117;
    color: white;
}

[data-testid="stMetric"] {
    background-color: #161b22;
    border-radius: 10px;
    padding: 15px;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# TELEGRAM
# =========================================================

TOKEN = "8910102188:AAFAQGQKjIOUMB19HHYSQKC4-0fKly3ASxE"
CHAT_ID = "7790207379"

def send_telegram(message):

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": message
    }

    requests.post(url, data=data)

# =========================================================
# BINANCE FUTURES
# =========================================================

exchange = ccxt.binance({
    "enableRateLimit": True,
    "options": {
        "defaultType": "future"
    }
})

# =========================================================
# PAIRS
# =========================================================

pairs = [
    "BTC/USDT",
    "ETH/USDT",
    "XRP/USDT"
]

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("ICT AI BOT ULTRA")

selected_pair = st.sidebar.selectbox(
    "SELECT PAIR",
    pairs
)

# =========================================================
# GET DATA
# =========================================================

def get_data(symbol, timeframe):

    ohlcv = exchange.fetch_ohlcv(
        symbol,
        timeframe,
        limit=300
    )

    df = pd.DataFrame(
        ohlcv,
        columns=[
            "time",
            "open",
            "high",
            "low",
            "close",
            "volume"
        ]
    )

    return df

# =========================================================
# MULTI TIMEFRAME
# =========================================================

htf_df = get_data(selected_pair, "1h")
mtf_df = get_data(selected_pair, "15m")
ltf_df = get_data(selected_pair, "1m")

# =========================================================
# EMA
# =========================================================

ltf_df["ema20"] = ltf_df["close"].ewm(span=20).mean()
ltf_df["ema50"] = ltf_df["close"].ewm(span=50).mean()
ltf_df["ema200"] = ltf_df["close"].ewm(span=200).mean()

# =========================================================
# ATR
# =========================================================

ltf_df["tr"] = (
    ltf_df["high"] - ltf_df["low"]
)

atr = ltf_df["tr"].rolling(14).mean().iloc[-1]

# =========================================================
# VALUES
# =========================================================

last_close = ltf_df["close"].iloc[-1]
last_high = ltf_df["high"].iloc[-1]
last_low = ltf_df["low"].iloc[-1]

# =========================================================
# TREND
# =========================================================

bullish_trend = (
    ltf_df["ema20"].iloc[-1]
    >
    ltf_df["ema50"].iloc[-1]
    >
    ltf_df["ema200"].iloc[-1]
)

bearish_trend = (
    ltf_df["ema20"].iloc[-1]
    <
    ltf_df["ema50"].iloc[-1]
    <
    ltf_df["ema200"].iloc[-1]
)

# =========================================================
# BOS
# =========================================================

recent_high = ltf_df["high"].rolling(10).max().iloc[-2]
recent_low = ltf_df["low"].rolling(10).min().iloc[-2]

bos = "NONE"

if last_close > recent_high:
    bos = "BULLISH BOS"

if last_close < recent_low:
    bos = "BEARISH BOS"

# =========================================================
# ORDER BLOCK
# =========================================================

bullish_ob = False
bearish_ob = False

last_candle = ltf_df.iloc[-3]

if (
    last_candle["close"]
    <
    last_candle["open"]
    and
    last_close > last_candle["high"]
):
    bullish_ob = True

if (
    last_candle["close"]
    >
    last_candle["open"]
    and
    last_close < last_candle["low"]
):
    bearish_ob = True

# =========================================================
# FVG
# =========================================================

bullish_fvg = False
bearish_fvg = False

if (
    ltf_df["low"].iloc[-1]
    >
    ltf_df["high"].iloc[-3]
):
    bullish_fvg = True

if (
    ltf_df["high"].iloc[-1]
    <
    ltf_df["low"].iloc[-3]
):
    bearish_fvg = True

# =========================================================
# VOLUME
# =========================================================

avg_volume = (
    ltf_df["volume"]
    .rolling(20)
    .mean()
    .iloc[-1]
)

volume_confirmation = (
    ltf_df["volume"].iloc[-1]
    >
    avg_volume
)

# =========================================================
# KILLZONE
# =========================================================

current_hour = datetime.utcnow().hour

killzone = False

if 7 <= current_hour <= 10:
    killzone = True

if 13 <= current_hour <= 16:
    killzone = True

# =========================================================
# ENTRY
# =========================================================

entry = "NO ENTRY"

sl = 0
tp = 0

confidence = 0

# =========================================================
# BUY
# =========================================================

if (
    bullish_trend
    and bullish_ob
    and bullish_fvg
    and bos == "BULLISH BOS"
    and volume_confirmation
    and killzone
):

    entry = "BUY"

    sl = round(last_close - atr, 2)

    risk = abs(last_close - sl)

    tp = round(last_close + (risk * 3), 2)

# =========================================================
# SELL
# =========================================================

elif (
    bearish_trend
    and bearish_ob
    and bearish_fvg
    and bos == "BEARISH BOS"
    and volume_confirmation
    and killzone
):

    entry = "SELL"

    sl = round(last_close + atr, 2)

    risk = abs(last_close - sl)

    tp = round(last_close - (risk * 3), 2)

# =========================================================
# CONFIDENCE
# =========================================================

if bullish_trend or bearish_trend:
    confidence += 20

if bullish_ob or bearish_ob:
    confidence += 20

if bullish_fvg or bearish_fvg:
    confidence += 20

if volume_confirmation:
    confidence += 20

if bos != "NONE":
    confidence += 20

# =========================================================
# TELEGRAM DUPLICATE FIX
# =========================================================

signal_file = "last_signal.json"

current_signal = {
    "pair": selected_pair,
    "entry": entry,
    "price": round(last_close, 2)
}

send_alert = True

if os.path.exists(signal_file):

    with open(signal_file, "r") as f:

        old_signal = json.load(f)

    if old_signal == current_signal:

        send_alert = False

# =========================================================
# TELEGRAM ALERT
# =========================================================

if (
    (entry == "BUY" or entry == "SELL")
    and send_alert
):

    msg = f"""

ICT AI BOT ULTRA ALERT

PAIR: {selected_pair}

ENTRY: {entry}

ENTRY PRICE: {round(last_close, 2)}

STOP LOSS: {sl}

TAKE PROFIT: {tp}

BOS: {bos}

CONFIDENCE: {confidence}%

"""

    send_telegram(msg)

    with open(signal_file, "w") as f:

        json.dump(current_signal, f)

# =========================================================
# UI
# =========================================================

st.title("ICT AI BOT ULTRA PRO")

st.success(f"PAIR: {selected_pair}")

# =========================================================
# METRICS
# =========================================================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("ENTRY", entry)

with col2:
    st.metric("PRICE", round(last_close, 2))

with col3:
    st.metric("SL", sl)

with col4:
    st.metric("TP", tp)

# =========================================================
# AI CONFIDENCE
# =========================================================

st.markdown("## AI CONFIDENCE")

st.progress(confidence / 100)

st.metric("CONFIDENCE", f"{confidence}%")

# =========================================================
# MARKET STRUCTURE
# =========================================================

st.markdown("## MARKET STRUCTURE")

st.write("BOS:", bos)

st.write("BULLISH OB:", bullish_ob)

st.write("BEARISH OB:", bearish_ob)

st.write("BULLISH FVG:", bullish_fvg)

st.write("BEARISH FVG:", bearish_fvg)

# =========================================================
# CHART
# =========================================================

st.markdown("## LIVE CHART")

fig = go.Figure()

fig.add_trace(
    go.Candlestick(
        x=ltf_df.index,
        open=ltf_df["open"],
        high=ltf_df["high"],
        low=ltf_df["low"],
        close=ltf_df["close"],
        name="PRICE"
    )
)

# EMA

fig.add_trace(
    go.Scatter(
        x=ltf_df.index,
        y=ltf_df["ema20"],
        name="EMA20"
    )
)

fig.add_trace(
    go.Scatter(
        x=ltf_df.index,
        y=ltf_df["ema50"],
        name="EMA50"
    )
)

fig.add_trace(
    go.Scatter(
        x=ltf_df.index,
        y=ltf_df["ema200"],
        name="EMA200"
    )
)

# ENTRY ARROW

if entry == "BUY":

    fig.add_annotation(
        x=ltf_df.index[-1],
        y=last_close,
        text="BUY",
        showarrow=True
    )

if entry == "SELL":

    fig.add_annotation(
        x=ltf_df.index[-1],
        y=last_close,
        text="SELL",
        showarrow=True
    )

# FVG BOX

if bullish_fvg:

    fig.add_shape(
        type="rect",
        x0=ltf_df.index[-3],
        x1=ltf_df.index[-1],
        y0=ltf_df["high"].iloc[-3],
        y1=ltf_df["low"].iloc[-1]
    )

# UI

fig.update_layout(
    template="plotly_dark",
    height=850,
    xaxis_rangeslider_visible=False,
    paper_bgcolor="#0e1117",
    plot_bgcolor="#0e1117"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.caption("ICT AI BOT ULTRA PRO")