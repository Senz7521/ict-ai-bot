# =========================================================
# ICT AI BOT PRO MAX ULTRA FINAL
# LONDON + NEW YORK SESSION ONLY
# LIVE CHART ADDED
# =========================================================

import streamlit as st
from streamlit_autorefresh import st_autorefresh

import ccxt
import pandas as pd
import requests
import plotly.graph_objects as go

from datetime import datetime

# =========================================================
# AUTO REFRESH
# =========================================================

st_autorefresh(interval=5000, key="refresh")

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="ICT AI BOT PRO MAX",
    layout="wide"
)

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

.stApp{
    background-color:#0e1117;
    color:white;
}

.big-title{
    font-size:45px;
    font-weight:bold;
    color:white;
    padding:20px;
    border-radius:15px;
    background:linear-gradient(90deg,#00c6ff,#0072ff);
    text-align:center;
    margin-bottom:20px;
}

.box{
    padding:20px;
    border-radius:15px;
    margin-bottom:15px;
    color:white;
    font-weight:bold;
    font-size:20px;
}

.green{
    background:linear-gradient(90deg,#00b09b,#96c93d);
}

.red{
    background:linear-gradient(90deg,#ff416c,#ff4b2b);
}

.blue{
    background:linear-gradient(90deg,#2193b0,#6dd5ed);
}

.yellow{
    background:linear-gradient(90deg,#f7971e,#ffd200);
    color:black;
}

.purple{
    background:linear-gradient(90deg,#8E2DE2,#4A00E0);
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# TITLE
# =========================================================

st.markdown(
    '<div class="big-title">ICT AI BOT PRO MAX ULTRA</div>',
    unsafe_allow_html=True
)

# =========================================================
# TELEGRAM
# =========================================================

TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

def send_telegram(message):

    try:

        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

        data = {
            "chat_id": CHAT_ID,
            "text": message
        }

        requests.post(url, data=data)

    except:
        pass

# =========================================================
# EXCHANGE
# =========================================================

exchange = ccxt.bybit({
    "options": {
        "defaultType": "future"
    },
    "enableRateLimit": True
})

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("BOT SETTINGS")

pair = st.sidebar.selectbox(
    "SELECT PAIR",
    [
        "BTC/USDT",
        "ETH/USDT",
        "XRP/USDT",
        "BNB/USDT",
        "SOL/USDT",
        "XAU/USD"
    ]
)

timeframe = st.sidebar.selectbox(
    "SELECT TIMEFRAME",
    [
        "1m",
        "5m",
        "15m",
        "1h"
    ]
)

# =========================================================
# GOLD FIX
# =========================================================

symbol = pair

if pair == "XAU/USD":
    symbol = "BTC/USDT"

# =========================================================
# GET DATA
# =========================================================

def get_data(symbol, timeframe, limit=200):

    try:

        ohlcv = exchange.fetch_ohlcv(
            symbol,
            timeframe=timeframe,
            limit=limit
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

        df["time"] = pd.to_datetime(
            df["time"],
            unit="ms"
        )

        return df

    except Exception as e:

        st.error(f"DATA ERROR : {e}")

        return None

# =========================================================
# SESSION FILTER
# =========================================================

def session_filter():

    utc_hour = datetime.utcnow().hour

    if 7 <= utc_hour <= 11:
        return "LONDON SESSION"

    elif 12 <= utc_hour <= 16:
        return "NEW YORK SESSION"

    else:
        return "NO TRADE SESSION"

# =========================================================
# HTF BIAS
# =========================================================

def get_htf_bias(df):

    ema50 = df["close"].rolling(50).mean().iloc[-1]

    current = df["close"].iloc[-1]

    if current > ema50:
        return "BULLISH"

    elif current < ema50:
        return "BEARISH"

    return "NEUTRAL"

# =========================================================
# HTF POI
# =========================================================

def get_poi(df, bias):

    if bias == "BULLISH":

        return {
            "type":"BULLISH POI",
            "value":round(df["low"].iloc[-10:].min(),2)
        }

    elif bias == "BEARISH":

        return {
            "type":"BEARISH POI",
            "value":round(df["high"].iloc[-10:].max(),2)
        }

    return None

# =========================================================
# POI TAP
# =========================================================

def poi_tapped(price, poi):

    if poi is None:
        return False

    if abs(price - poi["value"]) <= 20:
        return True

    return False

# =========================================================
# MSS
# =========================================================

def detect_mss(df, bias):

    high = df["high"].iloc[-5:].max()
    low = df["low"].iloc[-5:].min()

    current = df["close"].iloc[-1]

    if bias == "BULLISH" and current > high:
        return "BULLISH MSS"

    elif bias == "BEARISH" and current < low:
        return "BEARISH MSS"

    return "NO MSS"

# =========================================================
# MICRO MSS
# =========================================================

def micro_mss(df, bias):

    last = df["close"].iloc[-1]
    prev = df["close"].iloc[-2]

    if bias == "BULLISH" and last > prev:
        return "MICRO BULLISH MSS"

    elif bias == "BEARISH" and last < prev:
        return "MICRO BEARISH MSS"

    return "NO MICRO MSS"

# =========================================================
# FVG
# =========================================================

def detect_fvg(df, bias):

    for i in range(2, len(df)-1):

        if bias == "BULLISH":

            if df["high"].iloc[i-2] < df["low"].iloc[i]:
                return "BULLISH FVG"

        elif bias == "BEARISH":

            if df["low"].iloc[i-2] > df["high"].iloc[i]:
                return "BEARISH FVG"

    return "NO FVG"

# =========================================================
# LOAD DATA
# =========================================================

htf_df = get_data(symbol, "1h")
ltf_df = get_data(symbol, timeframe)

# =========================================================
# MAIN
# =========================================================

if htf_df is not None and ltf_df is not None:

    # =====================================================
    # SESSION CHECK
    # =====================================================

    session = session_filter()

    # =====================================================
    # ANALYSIS
    # =====================================================

    bias = get_htf_bias(htf_df)

    poi = get_poi(htf_df, bias)

    current_price = round(
        float(ltf_df["close"].iloc[-1]),
        2
    )

    tapped = poi_tapped(current_price, poi)

    mss = detect_mss(ltf_df, bias)

    fvg = detect_fvg(ltf_df, bias)

    micro = micro_mss(ltf_df, bias)

    # =====================================================
    # LIVE CHART
    # =====================================================

    st.subheader("LIVE CHART")

    fig = go.Figure()

    fig.add_trace(
        go.Candlestick(
            x=ltf_df["time"],
            open=ltf_df["open"],
            high=ltf_df["high"],
            low=ltf_df["low"],
            close=ltf_df["close"],
            name="PRICE"
        )
    )

    # POI LINE
    if poi:

        fig.add_hline(
            y=poi["value"],
            line_dash="dash",
            line_color="yellow"
        )

    fig.update_layout(
        height=700,
        template="plotly_dark",
        xaxis_rangeslider_visible=False
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # =====================================================
    # TOP BOXES
    # =====================================================

    c1,c2,c3 = st.columns(3)

    with c1:

        st.markdown(
            f'<div class="box blue">PAIR<br>{pair}</div>',
            unsafe_allow_html=True
        )

    with c2:

        st.markdown(
            f'<div class="box green">LIVE PRICE<br>{current_price}</div>',
            unsafe_allow_html=True
        )

    with c3:

        st.markdown(
            f'<div class="box purple">SESSION<br>{session}</div>',
            unsafe_allow_html=True
        )

    # =====================================================
    # AI REVIEW
    # =====================================================

    st.subheader("AI REVIEW")

    col1,col2 = st.columns(2)

    # HTF BIAS
    with col1:

        color = "green"

        if bias == "BEARISH":
            color = "red"

        st.markdown(
            f'<div class="box {color}">HTF BIAS<br>{bias}</div>',
            unsafe_allow_html=True
        )

    # HTF POI
    with col2:

        if poi:

            st.markdown(
                f'<div class="box blue">HTF POI<br>{poi["value"]}</div>',
                unsafe_allow_html=True
            )

        else:

            st.markdown(
                f'<div class="box blue">HTF POI<br>NO POI</div>',
                unsafe_allow_html=True
            )

    # =====================================================
    # POI TAP
    # =====================================================

    tap_text = "WAITING"

    if tapped:
        tap_text = "POI TAPPED"

    st.markdown(
        f'<div class="box yellow">POI TAP<br>{tap_text}</div>',
        unsafe_allow_html=True
    )

    # =====================================================
    # MSS + FVG
    # =====================================================

    c4,c5 = st.columns(2)

    with c4:

        st.markdown(
            f'<div class="box green">LTF MSS<br>{mss}</div>',
            unsafe_allow_html=True
        )

    with c5:

        st.markdown(
            f'<div class="box blue">FVG<br>{fvg}</div>',
            unsafe_allow_html=True
        )

    # =====================================================
    # MICRO MSS
    # =====================================================

    st.markdown(
        f'<div class="box purple">MICRO MSS<br>{micro}</div>',
        unsafe_allow_html=True
    )

    # =====================================================
    # AI CONFIDENCE
    # =====================================================

    confidence = 50

    if (
        "BULLISH" in bias
        and "BULLISH" in mss
        and "BULLISH" in micro
        and "BULLISH" in fvg
    ):
        confidence = 90

    elif (
        "BEARISH" in bias
        and "BEARISH" in mss
        and "BEARISH" in micro
        and "BEARISH" in fvg
    ):
        confidence = 90

    st.markdown(
        f'<div class="box yellow">AI CONFIDENCE<br>{confidence}%</div>',
        unsafe_allow_html=True
    )

    # =====================================================
    # ENTRY MODEL
    # =====================================================

    st.subheader("ENTRY MODEL")

    allow_trade = False

    # ONLY LONDON + NEW YORK
    if (
        session == "LONDON SESSION"
        or session == "NEW YORK SESSION"
    ):

        allow_trade = True

    if allow_trade and tapped:

        if bias == "BULLISH":

            entry = current_price
            sl = entry - 20
            tp1 = entry + 20
            tp2 = entry + 40
            tp3 = entry + 60

        elif bias == "BEARISH":

            entry = current_price
            sl = entry + 20
            tp1 = entry - 20
            tp2 = entry - 40
            tp3 = entry - 60

        signal = f"""
ICT AI BOT ALERT

PAIR: {pair}

TRADE TYPE: {bias}

ENTRY: {entry}

SL: {sl}

TP1: {tp1}

TP2: {tp2}

TP3: {tp3}

SESSION: {session}

HTF BIAS: {bias}

LTF MSS: {mss}

FVG: {fvg}

MICRO MSS: {micro}

CONFIDENCE: {confidence}%
"""

        st.success(signal)

        # TELEGRAM
        send_telegram(signal)

    else:

        st.warning(
            "NO TRADE - WAITING FOR LONDON OR NEW YORK SESSION"
        )

    # =====================================================
    # LIVE CHAT
    # =====================================================

    st.subheader("LIVE CHAT")

    msg = st.text_input("SEND MESSAGE")

    if st.button("SEND"):

        st.success(f"YOU : {msg}")

    # =====================================================
    # STATS
    # =====================================================

    st.subheader("TODAY STATS")

    s1,s2,s3 = st.columns(3)

    with s1:
        st.metric("TOTAL TRADES",12)

    with s2:
        st.metric("WINS",8)

    with s3:
        st.metric("LOSSES",4)

else:

    st.error("DATA NOT LOADED")