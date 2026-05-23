import streamlit as st
import ccxt
import pandas as pd

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="ICT AI BOT",
    layout="wide"
)

# =========================================================
# EXCHANGE
# =========================================================

exchange = ccxt.binance({
    "options": {
        "defaultType": "future"
    }
})

# =========================================================
# SELECT PAIR
# =========================================================

selected_pair = st.selectbox(
    "SELECT PAIR",
    [
        "BTC/USDT",
        "ETH/USDT"
    ]
)

# =========================================================
# GET DATA
# =========================================================

def get_data(symbol, timeframe):

    ohlcv = exchange.fetch_ohlcv(
        symbol,
        timeframe,
        limit=100
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
# HTF BIAS
# =========================================================

def get_htf_bias(df):

    last_high = df["high"].iloc[-2]
    prev_high = df["high"].iloc[-5]

    last_low = df["low"].iloc[-2]
    prev_low = df["low"].iloc[-5]

    if last_high > prev_high:
        return "BULLISH"

    elif last_low < prev_low:
        return "BEARISH"

    return "NEUTRAL"

# =========================================================
# MSS
# =========================================================

def get_mss(df, bias):

    current_close = df["close"].iloc[-1]

    previous_high = df["high"].iloc[-3]
    previous_low = df["low"].iloc[-3]

    if bias == "BULLISH":

        if current_close > previous_high:
            return {
                "type": "BULLISH MSS",
                "valid": True
            }

    if bias == "BEARISH":

        if current_close < previous_low:
            return {
                "type": "BEARISH MSS",
                "valid": True
            }

    return {
        "type": "NO MSS",
        "valid": False
    }

# =========================================================
# FVG
# =========================================================

def get_fvg(df, bias):

    high1 = df["high"].iloc[-3]
    low3 = df["low"].iloc[-1]

    low1 = df["low"].iloc[-3]
    high3 = df["high"].iloc[-1]

    if bias == "BULLISH":

        if low3 > high1:

            return {
                "type": "BULLISH FVG",
                "valid": True
            }

    if bias == "BEARISH":

        if high3 < low1:

            return {
                "type": "BEARISH FVG",
                "valid": True
            }

    return {
        "type": "NO FVG",
        "valid": False
    }

# =========================================================
# ENTRY MODEL
# =========================================================

def get_entry(df, bias):

    current_price = df["close"].iloc[-1]

    if bias == "BULLISH":

        return {
            "entry": "BUY",
            "price": round(current_price, 2),
            "sl": round(current_price - 100, 2),
            "tp": round(current_price + 300, 2)
        }

    if bias == "BEARISH":

        return {
            "entry": "SELL",
            "price": round(current_price, 2),
            "sl": round(current_price + 100, 2),
            "tp": round(current_price - 300, 2)
        }

# =========================================================
# DATA
# =========================================================

htf_df = get_data(selected_pair, "15m")
ltf_df = get_data(selected_pair, "1m")

# =========================================================
# LOGIC
# =========================================================

bias = get_htf_bias(htf_df)

mss = get_mss(ltf_df, bias)

fvg = get_fvg(ltf_df, bias)

entry = get_entry(ltf_df, bias)

current_price = ltf_df["close"].iloc[-1]

# =========================================================
# TITLE
# =========================================================

st.title("ICT AI BOT")

st.success(f"ACTIVE PAIR: {selected_pair}")

st.metric(
    "LIVE PRICE",
    round(current_price, 2)
)

st.markdown("---")

# =========================================================
# HTF SECTION
# =========================================================

st.header("HTF ANALYSIS")

col1, col2 = st.columns(2)

with col1:

    st.subheader("HTF BIAS")

    if bias == "BULLISH":
        st.success(bias)

    elif bias == "BEARISH":
        st.error(bias)

    else:
        st.warning(bias)

with col2:

    st.subheader("HTF POI")

    st.info("ORDER BLOCK / FVG ZONE")

st.markdown("---")

# =========================================================
# LTF SECTION
# =========================================================

st.header("LTF CONFIRMATION")

col3, col4 = st.columns(2)

with col3:

    st.subheader("MSS")

    if mss["valid"]:
        st.success(mss["type"])

    else:
        st.warning("NO MSS")

with col4:

    st.subheader("FVG")

    if fvg["valid"]:
        st.success(fvg["type"])

    else:
        st.warning("NO FVG")

st.markdown("---")

# =========================================================
# ENTRY SECTION
# =========================================================

st.header("ENTRY MODEL")

if mss["valid"] and fvg["valid"]:

    st.success(f"""
    ENTRY: {entry["entry"]}

    PRICE: {entry["price"]}

    SL: {entry["sl"]}

    TP: {entry["tp"]}
    """)

else:

    st.error("NO VALID ENTRY")

# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.caption("ICT AI BOT PRO")