# =========================================================
# ICT AI BOT PRO
# =========================================================

# =========================================================
# IMPORTS
# =========================================================

import streamlit as st
import ccxt
import pandas as pd

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="ICT AI BOT PRO",
    layout="wide"
)

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
# ENTRY
# =========================================================

entry = "NO ENTRY"

sl = 0
tp = 0

if (
    htf_bias == "BULLISH"
    and poi_tap == "POI TAPPED"
    and ltf_mss == "BULLISH MSS"
    and fvg == "BULLISH FVG"
    and micro_mss == "MICRO BULLISH MSS"
):

    entry = "BUY"

    sl = round(last_close - 10, 2)
    tp = round(last_close + 25, 2)

if (
    htf_bias == "BEARISH"
    and poi_tap == "POI TAPPED"
    and ltf_mss == "BEARISH MSS"
    and fvg == "BEARISH FVG"
    and micro_mss == "MICRO BEARISH MSS"
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
    Liquidity taken.
    MSS confirmed.
    FVG confirmed.
    Buy probability high.
    """

elif entry == "SELL":

    ai_review = """
    Bearish structure aligned.
    Liquidity taken.
    MSS confirmed.
    FVG confirmed.
    Sell probability high.
    """

else:

    ai_review = """
    Market structure incomplete.
    Waiting for confirmation.
    """

# =========================================================
# TITLE
# =========================================================

st.title("ICT AI BOT PRO")

st.success(f"ACTIVE PAIR: {selected_pair}")

# =========================================================
# MARKET ANALYSIS BOX
# =========================================================

st.markdown("## MARKET ANALYSIS")

market_box = st.container(border=True)

with market_box:

    st.write("PAIR:", selected_pair)

    st.write("CURRENT PRICE:", round(last_close, 2))

    st.write("LIQUIDITY:", sweep)

# =========================================================
# AI REVIEW BOX
# =========================================================

st.markdown("## AI REVIEW")

review_box = st.container(border=True)

with review_box:

    st.write(ai_review)

# =========================================================
# HTF BOXES
# =========================================================

col1, col2 = st.columns(2)

with col1:

    htf_bias_box = st.container(border=True)

    with htf_bias_box:

        st.subheader("HTF BIAS")

        if htf_bias == "BULLISH":
            st.success(htf_bias)
        else:
            st.error(htf_bias)

with col2:

    htf_poi_box = st.container(border=True)

    with htf_poi_box:

        st.subheader("HTF POI")

        st.info(htf_poi)

# =========================================================
# POI TAP BOX
# =========================================================

st.markdown("## HTF POI TAP")

poi_box = st.container(border=True)

with poi_box:

    if poi_tap == "POI TAPPED":
        st.success(poi_tap)
    else:
        st.warning(poi_tap)

# =========================================================
# LTF MSS + FVG
# =========================================================

col3, col4 = st.columns(2)

with col3:

    ltf_box = st.container(border=True)

    with ltf_box:

        st.subheader("LTF MSS")

        if "BULLISH" in ltf_mss:
            st.success(ltf_mss)

        elif "BEARISH" in ltf_mss:
            st.error(ltf_mss)

        else:
            st.warning(ltf_mss)

with col4:

    fvg_box = st.container(border=True)

    with fvg_box:

        st.subheader("FVG")

        st.info(fvg)

# =========================================================
# MICRO MSS BOX
# =========================================================

st.markdown("## MICRO MSS")

micro_box = st.container(border=True)

with micro_box:

    st.success(micro_mss)

# =========================================================
# ENTRY BOX
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

st.markdown("## LIVE CHART")

st.line_chart(ltf_df["close"])

# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.caption("ICT AI BOT PRO")