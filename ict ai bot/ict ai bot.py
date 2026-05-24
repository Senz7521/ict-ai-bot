# =========================================================
# ICT AI BOT ULTRA PRO
# LIVE CHART + BTC ETH GOLD SELECTOR
# HTF / LTF / MSS / FVG SEPARATE BOXES
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
from datetime import datetime

# =========================================================
# AUTO REFRESH
# =========================================================

st_autorefresh(interval=5000, key="refresh")

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="ICT AI BOT ULTRA",
    layout="wide"
)

st.title("ICT AI BOT ULTRA")

# =========================================================
# TELEGRAM
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
# SYMBOL OPTIONS
# =========================================================

SYMBOLS = {
    "BTC": "BTC/USDT",
    "ETH": "ETH/USDT",
    "GOLD": "BTC/USDT"
}

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("PAIR SETTINGS")

pair_name = st.sidebar.selectbox(
    "SELECT PAIR",
    list(SYMBOLS.keys())
)

symbol = SYMBOLS[pair_name]

ltf_tf = st.sidebar.selectbox(
    "LTF",
    ["1m", "5m"],
    index=0
)

htf_tf = st.sidebar.selectbox(
    "HTF",
    ["15m", "1h", "4h"],
    index=0
)

# =========================================================
# FETCH DATA
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

        st.error(e)

        return None

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
# HTF POI
# =========================================================

def get_htf_poi(df, bias):

    candle = df.iloc[-3]

    if bias == "BULLISH":

        return {
            "type": "BULLISH OB",
            "high": candle["high"],
            "low": candle["low"]
        }

    elif bias == "BEARISH":

        return {
            "type": "BEARISH OB",
            "high": candle["high"],
            "low": candle["low"]
        }

    return None

# =========================================================
# LTF MSS
# =========================================================

def get_ltf_mss(df, bias):

    current_close = df["close"].iloc[-1]

    swing_high = df["high"].iloc[-5:-1].max()
    swing_low = df["low"].iloc[-5:-1].min()

    if bias == "BULLISH":

        if current_close > swing_high:
            return "BULLISH MSS"

    elif bias == "BEARISH":

        if current_close < swing_low:
            return "BEARISH MSS"

    return "NO MSS"

# =========================================================
# MICRO FVG
# =========================================================

def get_micro_fvg(df, bias):

    for i in range(2, len(df)-1):

        # BULLISH
        if bias == "BULLISH":

            if df["high"].iloc[i-2] < df["low"].iloc[i]:

                return "BULLISH FVG"

        # BEARISH
        elif bias == "BEARISH":

            if df["low"].iloc[i-2] > df["high"].iloc[i]:

                return "BEARISH FVG"

    return "NO FVG"

# =========================================================
# ENTRY MODEL
# =========================================================

def get_entry(df, bias):

    price = df["close"].iloc[-1]

    if bias == "BULLISH":

        return {
            "type": "BUY",
            "entry": round(price, 2),
            "sl": round(price - 100, 2),
            "tp": round(price + 300, 2)
        }

    elif bias == "BEARISH":

        return {
            "type": "SELL",
            "entry": round(price, 2),
            "sl": round(price + 100, 2),
            "tp": round(price - 300, 2)
        }

    return None

# =========================================================
# GET DATA
# =========================================================

htf_df = get_data(symbol, htf_tf)
ltf_df = get_data(symbol, ltf_tf)

# =========================================================
# MAIN
# =========================================================

if htf_df is not None and ltf_df is not None:

    # =====================================================
    # ANALYSIS
    # =====================================================

    htf_bias = get_htf_bias(htf_df)

    htf_poi = get_htf_poi(htf_df, htf_bias)

    ltf_mss = get_ltf_mss(ltf_df, htf_bias)

    micro_fvg = get_micro_fvg(ltf_df, htf_bias)

    entry = None

    if (
        "BULLISH" in htf_bias
        and "BULLISH" in ltf_mss
        and "BULLISH" in micro_fvg
    ):

        entry = get_entry(ltf_df, "BULLISH")

    elif (
        "BEARISH" in htf_bias
        and "BEARISH" in ltf_mss
        and "BEARISH" in micro_fvg
    ):

        entry = get_entry(ltf_df, "BEARISH")

    # =====================================================
    # LIVE CHART
    # =====================================================

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

    # HTF POI LINES
    if htf_poi:

        fig.add_hline(
            y=htf_poi["high"],
            line_dash="dash"
        )

        fig.add_hline(
            y=htf_poi["low"],
            line_dash="dash"
        )

    fig.update_layout(
        height=700,
        xaxis_rangeslider_visible=False
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # =====================================================
    # BOXES
    # =====================================================

    col1, col2, col3 = st.columns(3)

    with col1:

        st.info("HTF BIAS")
        st.write(htf_bias)

    with col2:

        st.info("HTF POI")

        if htf_poi:

            st.write(htf_poi["type"])
            st.write(f"HIGH : {htf_poi['high']}")
            st.write(f"LOW : {htf_poi['low']}")

    with col3:

        st.info("LTF MSS")
        st.write(ltf_mss)

    # =====================================================
    # SECOND ROW
    # =====================================================

    col4, col5, col6 = st.columns(3)

    with col4:

        st.info("MICRO FVG")
        st.write(micro_fvg)

    with col5:

        st.info("PAIR")
        st.write(pair_name)

    with col6:

        st.info("SESSION")

        utc_hour = datetime.utcnow().hour

        if 7 <= utc_hour <= 11:
            st.write("LONDON")

        elif 12 <= utc_hour <= 16:
            st.write("NEW YORK")

        else:
            st.write("ASIAN")

    # =====================================================
    # ENTRY BOX
    # =====================================================

    st.subheader("FINAL ENTRY")

    if entry:

        st.success("ENTRY READY")

        st.write(f"TYPE : {entry['type']}")
        st.write(f"ENTRY : {entry['entry']}")
        st.write(f"SL : {entry['sl']}")
        st.write(f"TP : {entry['tp']}")

        msg = f"""
ICT AI BOT ALERT

PAIR : {pair_name}

ENTRY : {entry['type']}

ENTRY PRICE : {entry['entry']}

SL : {entry['sl']}

TP : {entry['tp']}

HTF BIAS : {htf_bias}

LTF MSS : {ltf_mss}

FVG : {micro_fvg}
"""

        send_telegram(msg)

    else:

        st.warning("WAITING FOR CONFIRMATION")

# =========================================================
# FOOTER
# =========================================================

st.markdown("---")
st.caption("ICT AI BOT ULTRA PRO")