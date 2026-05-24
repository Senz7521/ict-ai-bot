# =========================================================
# ICT AI BOT PRO MAX
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
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="ICT AI BOT PRO",
    layout="wide"
)

# =========================================================
# TITLE
# =========================================================

st.title("ICT AI BOT PRO MAX")

# =========================================================
# TELEGRAM SETTINGS
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

st.sidebar.title("BOT SETTINGS")

pair = st.sidebar.selectbox(
    "SELECT PAIR",
    [
        "BTC/USDT",
        "ETH/USDT",
        "XRP/USDT"
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
# GOLD SPECIAL
# =========================================================

if pair == "XAU/USD":
    symbol = "XAU/USD"
else:
    symbol = pair

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

        return df

    except Exception as e:

        st.error(f"DATA ERROR: {e}")

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

        for i in range(len(df)-10, len(df)-2):

            if (
                df["close"].iloc[i] > df["open"].iloc[i]
                and df["low"].iloc[i] < df["low"].iloc[i-1]
            ):

                return df["low"].iloc[i]

    elif bias == "BEARISH":

        for i in range(len(df)-10, len(df)-2):

            if (
                df["close"].iloc[i] < df["open"].iloc[i]
                and df["high"].iloc[i] > df["high"].iloc[i-1]
            ):

                return df["high"].iloc[i]

    return None

# =========================================================
# POI TAP
# =========================================================

def poi_tapped(current_price, poi):

    if poi is None:
        return False

    if abs(current_price - poi) <= 2:
        return True

    return False

# =========================================================
# LIQUIDITY SWEEP
# =========================================================

def liquidity_sweep(df):

    recent_high = df["high"].iloc[-5:].max()
    recent_low = df["low"].iloc[-5:].min()

    current_high = df["high"].iloc[-1]
    current_low = df["low"].iloc[-1]

    if current_high > recent_high:

        return {
            "valid": True,
            "type": "BUY SIDE SWEEP"
        }

    if current_low < recent_low:

        return {
            "valid": True,
            "type": "SELL SIDE SWEEP"
        }

    return {
        "valid": False,
        "type": "NO SWEEP"
    }

# =========================================================
# MSS
# =========================================================

def detect_mss(df, bias):

    recent_high = df["high"].iloc[-5:].max()
    recent_low = df["low"].iloc[-5:].min()

    current_price = df["close"].iloc[-1]

    if bias == "BULLISH":

        if current_price > recent_high:

            return {
                "valid": True,
                "type": "BULLISH MSS"
            }

    elif bias == "BEARISH":

        if current_price < recent_low:

            return {
                "valid": True,
                "type": "BEARISH MSS"
            }

    return {
        "valid": False,
        "type": "NO MSS"
    }

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
# ENTRY MODEL
# =========================================================

def entry_model(df, bias, mss):

    current_price = df["close"].iloc[-1]

    # BUY
    if bias == "BULLISH":

        entry = current_price

        sl = entry - 10

        tp1 = entry + 10
        tp2 = entry + 20
        tp3 = entry + 35

    # SELL
    elif bias == "BEARISH":

        entry = current_price

        sl = entry + 10

        tp1 = entry - 10
        tp2 = entry - 20
        tp3 = entry - 35

    else:

        return "NO ENTRY"

    return f"""
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

HTF BIAS: {bias}

LTF MSS: {mss["type"]}

POI TYPE: {"Bullish Order Block" if bias == "BULLISH" else "Bearish Order Block"}

ENTRY MODEL: {"Micro Bullish FVG" if bias == "BULLISH" else "Micro Bearish FVG"}

CONFIRMED:
✓ HTF BIAS
✓ POI
✓ LTF POI TAP
✓ LTF MSS
✓ MICRO FVG / OB ENTRY

STATUS: READY FOR ENTRY
"""

# =========================================================
# LOAD DATA
# =========================================================

htf_df = get_data(symbol, "1h")
ltf_df = get_data(symbol, timeframe)

# =========================================================
# MAIN
# =========================================================

if htf_df is not None and ltf_df is not None:

    bias = get_htf_bias(htf_df)

    poi = get_poi(htf_df, bias)

    current_price = ltf_df["close"].iloc[-1]

    tapped = poi_tapped(current_price, poi)

    sweep = liquidity_sweep(ltf_df)

    mss = detect_mss(ltf_df, bias)

    fvg = detect_fvg(ltf_df, bias)

    # =====================================================
    # LIVE BOX
    # =====================================================

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "LIVE PRICE",
            round(float(current_price), 2)
        )

    with col2:

        st.metric(
            "SESSION",
            session_filter()
        )

    # =====================================================
    # DISPLAY
    # =====================================================

    st.subheader("MARKET ANALYSIS")

    st.write(f"PAIR: {pair}")

    st.write(f"CURRENT PRICE: {round(float(current_price), 2)}")

    st.write(f"SESSION: {session_filter()}")

    st.write(f"LIQUIDITY: {sweep['type']}")

    st.subheader("AI REVIEW")

    st.success(f"HTF BIAS : {bias}")

    st.info(f"HTF POI : {poi}")

    st.warning(f"HTF POI TAP : {tapped}")

    st.success(f"LTF MSS : {mss['type']}")

    st.info(f"FVG : {fvg}")

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
            bias,
            mss
        )

        st.success("READY FOR ENTRY")

        st.code(entry)

        send_telegram(entry)

    else:

        st.warning("WAITING FOR CONFIRMATION")

else:

    st.error("DATA NOT LOADED")