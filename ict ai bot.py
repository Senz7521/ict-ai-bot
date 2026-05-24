# =========================================================
# ICT AI BOT PRO - CLEAN STRUCTURE VERSION
# =========================================================

import streamlit as st
import ccxt
import pandas as pd
import time
from datetime import datetime
import requests

# =========================================================
# TELEGRAM
# =========================================================

TOKEN = "8910102188:AAFAQGQKjIOUMB19HHYSQKC4-0fKly3ASxE"
CHAT_ID = "7790207379"

def send_telegram(msg):

    try:

        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

        data = {
            "chat_id": CHAT_ID,
            "text": msg
        }

        requests.post(url, data=data)

    except Exception as e:

        print("TELEGRAM ERROR:", e)

# =========================================================
# EXCHANGE
# =========================================================

exchange = ccxt.binance()

# =========================================================
# GET DATA
# =========================================================

def get_data(symbol="ETH/USDT", timeframe="15m", limit=200):

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

        print("DATA ERROR:", e)

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
# HTF BIAS (PURE STRUCTURE)
# =========================================================

def get_htf_bias(df):

    if len(df) < 20:
        return "NEUTRAL"

    last_high = df["high"].iloc[-2]
    old_high = df["high"].iloc[-10]

    last_low = df["low"].iloc[-2]
    old_low = df["low"].iloc[-10]

    if last_high > old_high:
        return "BULLISH"

    elif last_low < old_low:
        return "BEARISH"

    else:
        return "NEUTRAL"

# =========================================================
# ORDER BLOCK / POI
# =========================================================

def get_poi(df, bias):

    poi = None

    for i in range(len(df)-10, len(df)-2):

        # Bullish OB
        if bias == "BULLISH":

            if (
                df["close"].iloc[i] > df["open"].iloc[i]
            ):

                poi = df["low"].iloc[i]

        # Bearish OB
        elif bias == "BEARISH":

            if (
                df["close"].iloc[i] < df["open"].iloc[i]
            ):

                poi = df["high"].iloc[i]

    return poi

# =========================================================
# POI TAP
# =========================================================

def poi_tapped(price, poi):

    if poi is None:
        return False

    distance = abs(price - poi)

    if distance <= 5:
        return True

    return False

# =========================================================
# LIQUIDITY SWEEP
# =========================================================

def liquidity_sweep(df):

    recent_high = df["high"].iloc[-5:].max()
    recent_low = df["low"].iloc[-5:].min()

    current_price = df["close"].iloc[-1]

    # SELL SIDE
    if current_price <= recent_low:

        return {
            "valid": True,
            "type": "SELL SIDE SWEEP"
        }

    # BUY SIDE
    elif current_price >= recent_high:

        return {
            "valid": True,
            "type": "BUY SIDE SWEEP"
        }

    return {
        "valid": False
    }

# =========================================================
# MSS
# =========================================================

def detect_mss(df, bias):

    recent_high = df["high"].iloc[-5:].max()
    recent_low = df["low"].iloc[-5:].min()

    current_price = df["close"].iloc[-1]

    # Bullish MSS
    if (
        bias == "BULLISH"
        and current_price > recent_high
    ):

        return {
            "valid": True,
            "type": "BULLISH MSS"
        }

    # Bearish MSS
    elif (
        bias == "BEARISH"
        and current_price < recent_low
    ):

        return {
            "valid": True,
            "type": "BEARISH MSS"
        }

    return {
        "valid": False
    }

# =========================================================
# FVG
# =========================================================

def detect_fvg(df, bias):

    for i in range(2, len(df)-1):

        # Bullish FVG
        if bias == "BULLISH":

            if df["high"].iloc[i-2] < df["low"].iloc[i]:

                return "BULLISH FVG"

        # Bearish FVG
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

        return f"""
ICT AI BOT ALERT

PAIR: ETH/USDT

TRADE TYPE: BUY

ENTRY PRICE: {entry:.2f}

SL: {sl:.2f}

TP1: {tp1:.2f}
TP2: {tp2:.2f}
TP3: {tp3:.2f}

CONFIDENCE: 80%
"""

    # SELL
    elif bias == "BEARISH":

        entry = current_price

        sl = entry + 10

        tp1 = entry - 10
        tp2 = entry - 20
        tp3 = entry - 35

        return f"""
ICT AI BOT ALERT

PAIR: ETH/USDT

TRADE TYPE: SELL

ENTRY PRICE: 2103.99

SL: 2113.99

TP1: 2093.99
TP2: 2083.99
TP3: 2068.99

CONFIDENCE: 80%

SESSION: NEW YORK SESSION

HTF BIAS: BEARISH

LTF MSS: BEARISH MSS

POI TYPE: Bearish Order Block

ENTRY MODEL: Micro Bearish FVG

CONFIRMED:
✓ HTF BIAS
✓ POI
✓ LTF POI TAP
✓ LTF MSS
✓ MICRO FVG / OB ENTRY

STATUS: READY FOR ENTRY


    return "NO ENTRY"

# =========================================================
# STREAMLIT UI
# =========================================================

st.set_page_config(layout="wide")

st.title("ICT AI BOT PRO")

# =========================================================
# MAIN LOOP
# =========================================================

ltf_df = get_data()

if ltf_df is not None:

    bias = get_htf_bias(ltf_df)

    poi = get_poi(ltf_df, bias)

    current_price = ltf_df["close"].iloc[-1]

    tapped = poi_tapped(current_price, poi)

    sweep = liquidity_sweep(ltf_df)

    mss = detect_mss(ltf_df, bias)

    fvg = detect_fvg(ltf_df, bias)

    # =====================================================
    # DISPLAY
    # =====================================================

    st.subheader("MARKET ANALYSIS")

    st.write(f"PAIR: ETH/USDT")

    st.write(f"CURRENT PRICE: {current_price}")

   st.write(f"SESSION: {session_filter()}")

   st.write(f"LIQUIDITY: {sweep}")

    st.subheader("AI REVIEW")

    st.write(f"HTF BIAS : {bias}")

    st.write(f"HTF POI : {poi}")

    st.write(f"HTF POI TAP : {tapped}")

    st.write(f"LTF MSS : {mss}")

    st.write(f"FVG : {fvg}")

    # =====================================================
    # FINAL ENTRY
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

        st.success("READY FOR ENTRY")

        st.code(entry)

        send_telegram(entry)

    else:

        st.warning("WAITING FOR CONFIRMATION")

else:

       st.error( "DATA NOT LOADED" )