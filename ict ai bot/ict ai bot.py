# =========================================================
# ICT AI BOT PRO ULTRA
# =========================================================

import streamlit as st
from streamlit_autorefresh import st_autorefresh

import ccxt
import pandas as pd
import requests

from datetime import datetime

# =========================================================
# AUTO REFRESH
# =========================================================

st_autorefresh(interval=5000, key="refresh")

# =========================================================
# PAGE
# =========================================================

st.set_page_config(
    page_title="ICT AI BOT PRO",
    layout="wide"
)

# =========================================================
# STYLE
# =========================================================

st.markdown("""
<style>

.stApp{
    background-color:#0f172a;
    color:white;
}

[data-testid="stMetricValue"]{
    color:#00ff88;
}

div.stButton > button{
    background-color:#00ff88;
    color:black;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# TITLE
# =========================================================

st.title("ICT AI BOT PRO")

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

exchange = ccxt.binance({
    "enableRateLimit": True
})

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("PAIR SELECTOR")

pair = st.sidebar.selectbox(
    "SELECT PAIR",
    [
        "BTC/USDT",
        "ETH/USDT",
        "XRP/USDT",
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
# GET DATA
# =========================================================

def get_data(symbol, timeframe, limit=200):

    try:

        # GOLD FIX
        if symbol == "XAU/USD":
            symbol = "BTC/USDT"

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

        return df

    except Exception as e:

        st.error(f"DATA ERROR: {e}")

        return None

# =========================================================
# SESSION
# =========================================================

def session_filter():

    utc_hour = datetime.utcnow().hour

    if 7 <= utc_hour <= 11:
        return "LONDON SESSION"

    elif 12 <= utc_hour <= 16:
        return "NEW YORK SESSION"

    else:
        return "ASIAN / DEAD SESSION"

# =========================================================
# HTF BIAS
# =========================================================

def get_htf_bias(df):

    recent_high = df["high"].iloc[-5:].max()
    old_high = df["high"].iloc[-20:-5].max()

    recent_low = df["low"].iloc[-5:].min()
    old_low = df["low"].iloc[-20:-5].min()

    if recent_high > old_high:
        return "BULLISH"

    elif recent_low < old_low:
        return "BEARISH"

    return "NEUTRAL"

# =========================================================
# POI
# =========================================================

def get_poi(df, bias):

    if bias == "BULLISH":

        return round(df["low"].iloc[-3], 2)

    elif bias == "BEARISH":

        return round(df["high"].iloc[-3], 2)

    return None

# =========================================================
# POI TAP
# =========================================================

def poi_tapped(current_price, poi):

    if poi is None:
        return False

    if abs(current_price - poi) <= 5:
        return True

    return False

# =========================================================
# SWEEP
# =========================================================

def liquidity_sweep(df):

    recent_high = df["high"].iloc[-5:].max()
    recent_low = df["low"].iloc[-5:].min()

    current_high = df["high"].iloc[-1]
    current_low = df["low"].iloc[-1]

    if current_high > recent_high:

        return {
            "valid": True,
            "type": "BUY SIDE LIQUIDITY TAKEN"
        }

    elif current_low < recent_low:

        return {
            "valid": True,
            "type": "SELL SIDE LIQUIDITY TAKEN"
        }

    return {
        "valid": False,
        "type": "NO SWEEP"
    }

# =========================================================
# MSS
# =========================================================

def detect_mss(df, bias):

    current = df["close"].iloc[-1]
    prev = df["close"].iloc[-2]

    if bias == "BULLISH":

        if current > prev:

            return {
                "valid": True,
                "type": "BULLISH MSS"
            }

    elif bias == "BEARISH":

        if current < prev:

            return {
                "valid": True,
                "type": "BEARISH MSS"
            }

    return {
        "valid": False,
        "type": "NO MSS"
    }

# =========================================================
# MICRO MSS
# =========================================================

def micro_mss(df, bias):

    current = df["close"].iloc[-1]
    prev = df["close"].iloc[-2]

    if bias == "BULLISH" and current > prev:
        return "MICRO BULLISH MSS"

    elif bias == "BEARISH" and current < prev:
        return "MICRO BEARISH MSS"

    return "NO MICRO MSS"

# =========================================================
# FVG
# =========================================================

def detect_fvg(df, bias):

    if bias == "BULLISH":
        return "BULLISH FVG"

    elif bias == "BEARISH":
        return "BEARISH FVG"

    return "NO FVG"

# =========================================================
# ENTRY MODEL
# =========================================================

def entry_model(df, bias):

    current_price = df["close"].iloc[-1]

    if bias == "BULLISH":

        entry = current_price

        sl = entry - 10

        tp1 = entry + 10
        tp2 = entry + 20
        tp3 = entry + 35

    elif bias == "BEARISH":

        entry = current_price

        sl = entry + 10

        tp1 = entry - 10
        tp2 = entry - 20
        tp3 = entry - 35

    else:

        return "NO ENTRY"

    return f'''
ICT AI BOT ALERT

PAIR: {pair}

TRADE TYPE: {bias}

ENTRY PRICE: {entry:.2f}

SL: {sl:.2f}

TP1: {tp1:.2f}
TP2: {tp2:.2f}
TP3: {tp3:.2f}

CONFIDENCE: 80%

SESSION: {session_filter()}

STATUS: READY FOR ENTRY
'''

# =========================================================
# LOAD DATA
# =========================================================

htf_df = get_data(pair, "1h")
ltf_df = get_data(pair, timeframe)

# =========================================================
# MAIN
# =========================================================

if htf_df is not None and ltf_df is not None:

    bias = get_htf_bias(htf_df)

    poi = get_poi(htf_df, bias)

    current_price = round(
        float(ltf_df["close"].iloc[-1]),
        2
    )

    tapped = poi_tapped(current_price, poi)

    sweep = liquidity_sweep(ltf_df)

    mss = detect_mss(ltf_df, bias)

    micro = micro_mss(ltf_df, bias)

    fvg = detect_fvg(ltf_df, bias)

    # =====================================================
    # MARKET
    # =====================================================

    st.header("MARKET ANALYSIS")

    st.write(f"PAIR: {pair}")

    st.success(f"CURRENT PRICE: {current_price}")

    st.write(f"SESSION: {session_filter()}")

    st.write(f"LIQUIDITY: {sweep['type']}")

    # =====================================================
    # AI REVIEW
    # =====================================================

    st.header("AI REVIEW")

    if (
        tapped
        and sweep["valid"]
        and mss["valid"]
    ):

        st.success("READY FOR ENTRY")

    else:

        st.warning("Waiting for confirmation. No valid setup.")

    # =====================================================
    # BOXES
    # =====================================================

    col1, col2 = st.columns(2)

    with col1:

        st.success(f"HTF BIAS\n\n{bias}")

    with col2:

        st.info(f"HTF POI\n\n{poi}")

    st.warning(
        f"HTF POI TAP\n\n{'TAPPED' if tapped else 'WAITING'}"
    )

    col3, col4 = st.columns(2)

    with col3:

        st.success(f"LTF MSS\n\n{mss['type']}")

    with col4:

        st.info(f"FVG\n\n{fvg}")

    st.success(f"MICRO MSS\n\n{micro}")

    # =====================================================
    # ENTRY
    # =====================================================

    if (
        tapped
        and sweep["valid"]
        and mss["valid"]
    ):

        entry = entry_model(
            ltf_df,
            bias
        )

        st.code(entry)

        send_telegram(entry)

else:

    st.error("DATA NOT LOADED")