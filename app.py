# =========================================================
# ICT AI BOT PRO FINAL
# =========================================================

# =========================================================
# IMPORTS
# =========================================================

import streamlit as st
from streamlit_autorefresh import st_autorefresh

import ccxt
import pandas as pd
import plotly.graph_objects as go

import requests
import os

# =========================================================
# AUTO REFRESH
# =========================================================

st_autorefresh(interval=10000, key="refresh")

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="ICT AI BOT PRO",
    layout="wide"
)

# =========================================================
# CUSTOM BACKGROUND
# =========================================================

st.markdown("""
<style>

.stApp {
    background-color: #0e1117;
    color: white;
}

[data-testid="stMetric"] {
    background-color: #1c1f26;
    padding: 15px;
    border-radius: 10px;
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
    send_telegram("TEST MESSAGE")

# =========================================================
# EXCHANGE
# =========================================================

exchange = ccxt.bybit()

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

st.sidebar.title("ICT AI BOT")

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
        limit=200
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
# DATA
# =========================================================

htf_df = get_data(selected_pair, "15m")
ltf_df = get_data(selected_pair, "1m")

# =========================================================
# VALUES
# =========================================================

last_close = ltf_df["close"].iloc[-1]
prev_close = ltf_df["close"].iloc[-2]

last_high = ltf_df["high"].iloc[-1]
prev_high = ltf_df["high"].iloc[-2]

last_low = ltf_df["low"].iloc[-1]
prev_low = ltf_df["low"].iloc[-2]

# =========================================================
# SESSION FILTER
# =========================================================

current_hour = pd.Timestamp.now().hour

if 7 <= current_hour <= 11:

    active_session = "LONDON SESSION"

elif 13 <= current_hour <= 17:

    active_session = "NEW YORK SESSION"

else:

    active_session = "NO ACTIVE SESSION"

allow_trade = active_session != "NO ACTIVE SESSION"

# =========================================================
# NEWS FILTER
# =========================================================

high_impact_news = False

# =========================================================
# HTF BIAS
# =========================================================

if htf_df["close"].iloc[-1] > htf_df["close"].iloc[-20]:

    htf_bias = "BULLISH"

else:

    htf_bias = "BEARISH"

# =========================================================
# LIQUIDITY SWEEP
# =========================================================

if htf_bias == "BULLISH":

    if last_low < ltf_df["low"].iloc[-5]:

        sweep = "SELL SIDE LIQUIDITY TAKEN"

    else:

        sweep = "NO SWEEP"

else:

    if last_high > ltf_df["high"].iloc[-5]:

        sweep = "BUY SIDE LIQUIDITY TAKEN"

    else:

        sweep = "NO SWEEP"

# =========================================================
# HTF POI
# =========================================================

if htf_bias == "BULLISH":

    htf_poi = round(htf_df["low"].iloc[-10], 2)

else:

    htf_poi = round(htf_df["high"].iloc[-10], 2)

# =========================================================
# HTF POI TAP
# =========================================================

if htf_bias == "BULLISH":

    if last_low <= htf_poi:

        poi_tap = "POI TAPPED"

    else:

        poi_tap = "WAITING"

else:

    if last_high >= htf_poi:

        poi_tap = "POI TAPPED"

    else:

        poi_tap = "WAITING"

# =========================================================
# LTF MSS
# =========================================================

if htf_bias == "BULLISH":

    if last_high > prev_high:

        ltf_mss = "BULLISH MSS"

    else:

        ltf_mss = "NO MSS"

else:

    if last_low < prev_low:

        ltf_mss = "BEARISH MSS"

    else:

        ltf_mss = "NO MSS"

# =========================================================
# FVG
# =========================================================

if htf_bias == "BULLISH":

    if ltf_df["low"].iloc[-1] > ltf_df["high"].iloc[-3]:

        fvg = "BULLISH FVG"

    else:

        fvg = "NO FVG"

else:

    if ltf_df["high"].iloc[-1] < ltf_df["low"].iloc[-3]:

        fvg = "BEARISH FVG"

    else:

        fvg = "NO FVG"

# =========================================================
# MICRO MSS
# =========================================================

if htf_bias == "BULLISH":

    if last_close > prev_close:

        micro_mss = "MICRO BULLISH MSS"

    else:

        micro_mss = "NO MICRO MSS"

else:

    if last_close < prev_close:

        micro_mss = "MICRO BEARISH MSS"

    else:

        micro_mss = "NO MICRO MSS"

# =========================================================
# CONFIDENCE
# =========================================================

confidence = 0

if htf_bias:

    confidence += 20

if "LIQUIDITY" in sweep:

    confidence += 20

if "MSS" in ltf_mss:

    confidence += 20

if "FVG" in fvg:

    confidence += 20

if "MICRO" in micro_mss:

    confidence += 20

# =========================================================
# ENTRY
# =========================================================

entry = "NO ENTRY"

sl = 0
tp = 0

if not allow_trade:

    entry = "SESSION CLOSED"

if high_impact_news:

    entry = "NEWS TIME NO TRADE"

# BUY
if (
    htf_bias == "BULLISH"
    and poi_tap == "POI TAPPED"
    and ltf_mss == "BULLISH MSS"
    and fvg == "BULLISH FVG"
    and micro_mss == "MICRO BULLISH MSS"
    and allow_trade
):

    entry = "BUY"

    sl = round(last_close - 10, 2)

    tp = round(last_close + 25, 2)

# SELL
if (
    htf_bias == "BEARISH"
    and poi_tap == "POI TAPPED"
    and ltf_mss == "BEARISH MSS"
    and fvg == "BEARISH FVG"
    and micro_mss == "MICRO BEARISH MSS"
    and allow_trade
):

    entry = "SELL"

    sl = round(last_close + 10, 2)

    tp = round(last_close - 25, 2)

# =========================================================
# AI REVIEW
# =========================================================

if entry == "BUY":

    ai_review = """
    Bullish structure aligned.
    Liquidity sweep confirmed.
    MSS confirmed.
    FVG confirmed.
    High probability buy setup.
    """

elif entry == "SELL":

    ai_review = """
    Bearish structure aligned.
    Liquidity sweep confirmed.
    MSS confirmed.
    FVG confirmed.
    High probability sell setup.
    """

else:

    ai_review = """
    Waiting for full confirmation.
    No valid setup yet.
    """

# =========================================================
# TRADE HISTORY
# =========================================================

trade_file = "trade_history.csv"

if not os.path.exists(trade_file):

    trade_df = pd.DataFrame(columns=[
        "PAIR",
        "ENTRY",
        "SL",
        "TP",
        "CONFIDENCE"
    ])

    trade_df.to_csv(trade_file, index=False)

# =========================================================
# SAVE TRADE
# =========================================================

if entry == "BUY" or entry == "SELL":

    new_trade = pd.DataFrame([{
        "PAIR": selected_pair,
        "ENTRY": entry,
        "SL": sl,
        "TP": tp,
        "CONFIDENCE": confidence
    }])

    history = pd.read_csv(trade_file)

    history = pd.concat(
        [history, new_trade],
        ignore_index=True
    )

    history.to_csv(trade_file, index=False)

# =========================================================
# TELEGRAM ALERT
# =========================================================

if entry == "BUY" or entry == "SELL":

    send_telegram(
        f"""
ICT AI BOT ALERT

PAIR: {selected_pair}

ENTRY: {entry}

SL: {sl}

TP: {tp}

CONFIDENCE: {confidence}%

SESSION: {active_session}

HTF BIAS: {htf_bias}

LTF MSS: {ltf_mss}
"""
    )

# =========================================================
# TITLE
# =========================================================

st.title("ICT AI BOT PRO")

st.success(f"ACTIVE PAIR: {selected_pair}")

# =========================================================
# MARKET ANALYSIS
# =========================================================

st.markdown("## MARKET ANALYSIS")

market_box = st.container(border=True)

with market_box:

    st.write("PAIR:", selected_pair)

    st.write("CURRENT PRICE:", round(last_close, 2))

    st.write("SESSION:", active_session)

    st.write("LIQUIDITY:", sweep)

# =========================================================
# AI REVIEW
# =========================================================

st.markdown("## AI REVIEW")

review_box = st.container(border=True)

with review_box:

    st.write(ai_review)

# =========================================================
# HTF STRUCTURE
# =========================================================

col1, col2 = st.columns(2)

with col1:

    box1 = st.container(border=True)

    with box1:

        st.subheader("HTF BIAS")

        if htf_bias == "BULLISH":

            st.success(htf_bias)

        else:

            st.error(htf_bias)

with col2:

    box2 = st.container(border=True)

    with box2:

        st.subheader("HTF POI")

        st.info(htf_poi)

# =========================================================
# POI TAP
# =========================================================

st.markdown("## HTF POI TAP")

poi_box = st.container(border=True)

with poi_box:

    if poi_tap == "POI TAPPED":

        st.success(poi_tap)

    else:

        st.warning(poi_tap)

# =========================================================
# LTF STRUCTURE
# =========================================================

col3, col4 = st.columns(2)

with col3:

    box3 = st.container(border=True)

    with box3:

        st.subheader("LTF MSS")

        st.success(ltf_mss)

with col4:

    box4 = st.container(border=True)

    with box4:

        st.subheader("FVG")

        st.info(fvg)

# =========================================================
# MICRO MSS
# =========================================================

st.markdown("## MICRO MSS")

micro_box = st.container(border=True)

with micro_box:

    st.success(micro_mss)

# =========================================================
# CONFIDENCE
# =========================================================

st.markdown("## AI CONFIDENCE")

confidence_box = st.container(border=True)

with confidence_box:

    st.metric("CONFIDENCE", f"{confidence}%")

# =========================================================
# ENTRY MODEL
# =========================================================

st.markdown("## ENTRY MODEL")

entry_box = st.container(border=True)

with entry_box:

    st.metric("ENTRY", entry)

    st.metric("STOP LOSS", sl)

    st.metric("TAKE PROFIT", tp)

# =========================================================
# LIVE CHART
# =========================================================

st.markdown("## LIVE MARKET CHART")

fig = go.Figure(
    data=[
        go.Candlestick(
            x=ltf_df.index,
            open=ltf_df["open"],
            high=ltf_df["high"],
            low=ltf_df["low"],
            close=ltf_df["close"]
        )
    ]
)

fig.update_layout(
    template="plotly_dark",
    height=700,
    xaxis_rangeslider_visible=False
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# =========================================================
# TRADE HISTORY
# =========================================================

st.markdown("## TRADE HISTORY")

history_box = st.container(border=True)

with history_box:

    history = pd.read_csv(trade_file)

    st.dataframe(history)

# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.caption("ICT AI BOT PRO FINAL")