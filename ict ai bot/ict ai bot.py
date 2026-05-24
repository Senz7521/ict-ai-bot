# =========================================================
# ICT AI BOT PRO MAX
# LIVE CHART + GOLD CHART + TELEGRAM + STREAMLIT
# EMA REMOVED
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
import time
from datetime import datetime

# =========================================================
# AUTO REFRESH
# =========================================================

st_autorefresh(interval=10000, key="refresh")

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="ICT AI BOT",
    layout="wide"
)

st.title("ICT AI BOT PRO MAX")

# =========================================================
# TELEGRAM SETTINGS
# =========================================================

TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

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

exchange = ccxt.bybit({
    "options": {
        "defaultType": "future"
    },
    "enableRateLimit": True
})

# =========================================================
# SYMBOLS
# =========================================================

SYMBOLS = [
    "BTC/USDT",
    "ETH/USDT",
    "XRP/USDT",
    "SOL/USDT",
    "1000PEPE/USDT",
    "XAU/USD"
]

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("SETTINGS")

selected_symbol = st.sidebar.selectbox(
    "SELECT PAIR",
    SYMBOLS
)

timeframe = st.sidebar.selectbox(
    "TIMEFRAME",
    ["1m", "5m", "15m", "1h"],
    index=2
)

# =========================================================
# FETCH CANDLES
# =========================================================

def get_candles(symbol, timeframe, limit=200):

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

        df["time"] = pd.to_datetime(
            df["time"],
            unit="ms"
        )

        return df

    except Exception as e:

        st.error(f"CANDLE ERROR : {e}")

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

    recent_high = df["high"].iloc[-20:].max()
    recent_low = df["low"].iloc[-20:].min()

    current_price = df["close"].iloc[-1]

    middle = (recent_high + recent_low) / 2

    if current_price > middle:
        return "BULLISH"

    elif current_price < middle:
        return "BEARISH"

    return "NEUTRAL"

# =========================================================
# MSS DETECTION
# =========================================================

def detect_mss(df, bias):

    current_close = df["close"].iloc[-1]

    swing_high = df["high"].iloc[-5:-1].max()
    swing_low = df["low"].iloc[-5:-1].min()

    if bias == "BULLISH":

        if current_close > swing_high:

            return "BULLISH MSS"

    if bias == "BEARISH":

        if current_close < swing_low:

            return "BEARISH MSS"

    return "NO MSS"

# =========================================================
# FVG DETECTION
# =========================================================

def detect_fvg(df, bias):

    for i in range(2, len(df)-1):

        # BULLISH FVG
        if bias == "BULLISH":

            if df["high"].iloc[i-2] < df["low"].iloc[i]:

                return "BULLISH FVG"

        # BEARISH FVG
        elif bias == "BEARISH":

            if df["low"].iloc[i-2] > df["high"].iloc[i]:

                return "BEARISH FVG"

    return "NO FVG"

# =========================================================
# ORDER BLOCK
# =========================================================

def detect_ob(df, bias):

    if bias == "BULLISH":

        candle = df.iloc[-3]

        return {
            "type": "BULLISH OB",
            "high": candle["high"],
            "low": candle["low"]
        }

    elif bias == "BEARISH":

        candle = df.iloc[-3]

        return {
            "type": "BEARISH OB",
            "high": candle["high"],
            "low": candle["low"]
        }

    return None

# =========================================================
# ENTRY MODEL
# =========================================================

def entry_model(df, bias):

    price = df["close"].iloc[-1]

    if bias == "BULLISH":

        return {
            "ENTRY": "BUY",
            "PRICE": round(price, 2),
            "SL": round(price - 100, 2),
            "TP": round(price + 300, 2)
        }

    elif bias == "BEARISH":

        return {
            "ENTRY": "SELL",
            "PRICE": round(price, 2),
            "SL": round(price + 100, 2),
            "TP": round(price - 300, 2)
        }

    return None

# =========================================================
# GET DATA
# =========================================================

df = get_candles(selected_symbol, timeframe)

# =========================================================
# DATA CHECK
# =========================================================

if df is not None:

    # =====================================================
    # SESSION
    # =====================================================

    session = session_filter()

    # =====================================================
    # BIAS
    # =====================================================

    bias = get_htf_bias(df)

    # =====================================================
    # MSS
    # =====================================================

    mss = detect_mss(df, bias)

    # =====================================================
    # FVG
    # =====================================================

    fvg = detect_fvg(df, bias)

    # =====================================================
    # ORDER BLOCK
    # =====================================================

    ob = detect_ob(df, bias)

    # =====================================================
    # ENTRY
    # =====================================================

    entry = None

    if (
        "BULLISH" in bias
        and "BULLISH" in mss
        and "BULLISH" in fvg
    ):

        entry = entry_model(df, "BULLISH")

    elif (
        "BEARISH" in bias
        and "BEARISH" in mss
        and "BEARISH" in fvg
    ):

        entry = entry_model(df, "BEARISH")

    # =====================================================
    # LIVE CHART
    # =====================================================

    fig = go.Figure()

    fig.add_trace(
        go.Candlestick(
            x=df["time"],
            open=df["open"],
            high=df["high"],
            low=df["low"],
            close=df["close"],
            name="PRICE"
        )
    )

    # =====================================================
    # OB LINES
    # =====================================================

    if ob:

        fig.add_hline(
            y=ob["high"],
            line_dash="dash"
        )

        fig.add_hline(
            y=ob["low"],
            line_dash="dash"
        )

    # =====================================================
    # CHART SETTINGS
    # =====================================================

    fig.update_layout(
        height=700,
        xaxis_rangeslider_visible=False
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # =====================================================
    # INFO BOX
    # =====================================================

    col1, col2, col3 = st.columns(3)

    col1.metric("SESSION", session)
    col2.metric("HTF BIAS", bias)
    col3.metric("MSS", mss)

    # =====================================================
    # AI REVIEW
    # =====================================================

    st.subheader("AI REVIEW")

    st.write(f"PAIR : {selected_symbol}")
    st.write(f"TIMEFRAME : {timeframe}")
    st.write(f"HTF BIAS : {bias}")
    st.write(f"FVG : {fvg}")

    if ob:

        st.write(f"OB TYPE : {ob['type']}")
        st.write(f"OB HIGH : {ob['high']}")
        st.write(f"OB LOW : {ob['low']}")

    # =====================================================
    # FINAL ENTRY
    # =====================================================

    if entry:

        st.success("ENTRY READY")

        st.write(entry)

        msg = f"""
ICT AI BOT ALERT

PAIR : {selected_symbol}

ENTRY : {entry['ENTRY']}

PRICE : {entry['PRICE']}

SL : {entry['SL']}

TP : {entry['TP']}

SESSION : {session}

BIAS : {bias}

MSS : {mss}

FVG : {fvg}
"""

        send_telegram(msg)

    else:

        st.warning("WAITING FOR CONFIRMATION")

# =========================================================
# FOOTER
# =========================================================

st.markdown("---")
st.caption("ICT AI BOT PRO MAX")