# =========================================================
# ICT AI BOT PRO MAX ULTRA FINAL
# FULL PROFESSIONAL SMART MONEY VERSION
# =========================================================

# =========================================================
# IMPORTS
# =========================================================

import streamlit as st
from streamlit_autorefresh import st_autorefresh

import ccxt
import pandas as pd
import requests
import plotly.graph_objects as go

from datetime import datetime

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="ICT AI BOT PRO MAX ULTRA",
    layout="wide"
)

# =========================================================
# AUTO REFRESH
# =========================================================

st_autorefresh(interval=5000, key="refresh")

# =========================================================
# CSS
# =========================================================

st.markdown("""
<style>

.stApp{
    background:#0e1117;
    color:white;
}

.big-title{
    font-size:42px;
    font-weight:bold;
    padding:20px;
    border-radius:18px;
    background:linear-gradient(90deg,#00c6ff,#0072ff);
    text-align:center;
    margin-bottom:20px;
}

.box{
    padding:20px;
    border-radius:16px;
    margin-bottom:15px;
    color:white;
    font-size:18px;
    font-weight:bold;
    text-align:center;
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

.orange{
    background:linear-gradient(90deg,#ff8008,#ffc837);
    color:black;
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

TOKEN = "8854671551:AAGOwQ3waewFoQzadtwuJRBAVJNEOPKUkx0"
CHAT_ID = "5240659041"

if "last_signal" not in st.session_state:
    st.session_state.last_signal = ""

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
    "options":{
        "defaultType":"future"
    },
    "enableRateLimit":True
})

# =========================================================
# PAIRS
# =========================================================

PAIRS = {
    "BTC/USDT":"BTC/USDT",
    "ETH/USDT":"ETH/USDT",
    "XRP/USDT":"XRP/USDT",
    "BNB/USDT":"BNB/USDT",
    "SOL/USDT":"SOL/USDT",
    "XAU/USD":"XAUT/USDT"
}

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("BOT SETTINGS")

pair = st.sidebar.selectbox(
    "SELECT PAIR",
    list(PAIRS.keys())
)

symbol = PAIRS[pair]

ltf_timeframe = st.sidebar.selectbox(
    "SELECT TIMEFRAME",
    [
        "1m",
        "5m",
        "15m"
    ]
)

# =========================================================
# GET DATA
# =========================================================

def get_data(symbol,timeframe,limit=200):

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
# SESSION
# =========================================================

def session_filter():

    india_hour = datetime.now().hour

    if 5 <= india_hour < 12:
        return "TOKYO SESSION"

    elif 12 <= india_hour < 17:
        return "LONDON SESSION"

    elif 17 <= india_hour < 22:
        return "NEW YORK SESSION"

    return "NO TRADE SESSION"

# =========================================================
# HTF BIAS
# =========================================================

def get_htf_bias(df):

    swing_high = df["high"].iloc[-15:-5].max()
    swing_low = df["low"].iloc[-15:-5].min()

    current_close = df["close"].iloc[-1]

    if current_close > swing_high:
        return "BULLISH"

    elif current_close < swing_low:
        return "BEARISH"

    return "NEUTRAL"

# =========================================================
# ORDER BLOCK
# =========================================================

def order_block(df,bias):

    for i in range(len(df)-10,len(df)-2):

        if bias == "BULLISH":

            if (
                df["close"].iloc[i] < df["open"].iloc[i]
                and df["close"].iloc[i+1] > df["high"].iloc[i]
            ):

                return "BULLISH OB"

        elif bias == "BEARISH":

            if (
                df["close"].iloc[i] > df["open"].iloc[i]
                and df["close"].iloc[i+1] < df["low"].iloc[i]
            ):

                return "BEARISH OB"

    return "NO OB"

# =========================================================
# FVG
# =========================================================

def detect_fvg(df,bias):

    for i in range(2,len(df)-1):

        if bias == "BULLISH":

            if df["high"].iloc[i-2] < df["low"].iloc[i]:
                return "BULLISH FVG"

        elif bias == "BEARISH":

            if df["low"].iloc[i-2] > df["high"].iloc[i]:
                return "BEARISH FVG"

    return "NO FVG"

# =========================================================
# MSS
# =========================================================

def detect_mss(df,bias):

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
# MICRO MSS
# =========================================================

def micro_mss(df,bias):

    last_close = df["close"].iloc[-1]
    prev_close = df["close"].iloc[-2]

    if bias == "BULLISH":

        if last_close > prev_close:
            return "MICRO BULLISH MSS"

    elif bias == "BEARISH":

        if last_close < prev_close:
            return "MICRO BEARISH MSS"

    return "NO MICRO MSS"

# =========================================================
# DISPLACEMENT
# =========================================================

def displacement(df):

    candle_range = (
        df["high"].iloc[-1]
        - df["low"].iloc[-1]
    )

    avg_range = (
        (df["high"] - df["low"])
        .rolling(10)
        .mean()
        .iloc[-1]
    )

    if candle_range > avg_range * 1.5:
        return "VALID DISPLACEMENT"

    return "NO DISPLACEMENT"

# =========================================================
# PD ARRAY
# =========================================================

def pd_array(df):

    high = df["high"].iloc[-20:].max()
    low = df["low"].iloc[-20:].min()

    equilibrium = (high + low) / 2

    current = df["close"].iloc[-1]

    if current > equilibrium:
        return "PREMIUM"

    return "DISCOUNT"

# =========================================================
# LOAD DATA
# =========================================================

htf_4h = get_data(symbol,"4h")
htf_1h = get_data(symbol,"1h")
ltf_df = get_data(symbol,ltf_timeframe)

# =========================================================
# MAIN
# =========================================================

if htf_4h is not None and htf_1h is not None and ltf_df is not None:

    session = session_filter()

    bias_4h = get_htf_bias(htf_4h)
    bias_1h = get_htf_bias(htf_1h)

    if bias_4h == bias_1h:
        bias = bias_4h
    else:
        bias = "NEUTRAL"

    htf_poi = order_block(htf_4h,bias)

    ltf_fvg = detect_fvg(ltf_df,bias)

    ltf_mss = detect_mss(ltf_df,bias)

    ltf_micro = micro_mss(ltf_df,bias)

    displacement_signal = displacement(ltf_df)

    pd_zone = pd_array(htf_4h)

    current_price = round(
        float(ltf_df["close"].iloc[-1]),
        2
    )

    # =====================================================
    # AI SCORE
    # =====================================================

    score = 0

    if bias != "NEUTRAL":
        score += 20

    if "MSS" in ltf_mss:
        score += 20

    if "FVG" in ltf_fvg:
        score += 20

    if "VALID" in displacement_signal:
        score += 20

    if "MICRO" in ltf_micro:
        score += 20

    # =====================================================
    # STRICT ENTRY
    # =====================================================

    valid_trade = False

    if (
        bias != "NEUTRAL"
        and "OB" in htf_poi
        and "FVG" in ltf_fvg
        and "MSS" in ltf_mss
        and "MICRO" in ltf_micro
        and "VALID" in displacement_signal
        and score >= 80
    ):
        valid_trade = True

    # =====================================================
    # LIVE CHART
    # =====================================================

    st.subheader("LIVE SMART MONEY CHART")

    fig = go.Figure()

    fig.add_trace(
        go.Candlestick(
            x=ltf_df["time"],
            open=ltf_df["open"],
            high=ltf_df["high"],
            low=ltf_df["low"],
            close=ltf_df["close"],
            increasing_line_color="#00ff88",
            decreasing_line_color="#ff3355"
        )
    )

    fig.update_layout(
        template="plotly_dark",
        height=700,
        xaxis_rangeslider_visible=False,
        paper_bgcolor="#0e1117",
        plot_bgcolor="#0e1117"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # =====================================================
    # HTF ANALYSIS
    # =====================================================

    st.subheader("HTF ANALYSIS")

    h1,h2,h3,h4 = st.columns(4)

    with h1:
        st.markdown(f'<div class="box green">4H BIAS<br>{bias_4h}</div>', unsafe_allow_html=True)

    with h2:
        st.markdown(f'<div class="box blue">1H BIAS<br>{bias_1h}</div>', unsafe_allow_html=True)

    with h3:
        st.markdown(f'<div class="box purple">FINAL BIAS<br>{bias}</div>', unsafe_allow_html=True)

    with h4:
        st.markdown(f'<div class="box yellow">HTF POI<br>{htf_poi}</div>', unsafe_allow_html=True)

    # =====================================================
    # LTF ANALYSIS
    # =====================================================

    st.subheader("LTF ANALYSIS")

    l1,l2,l3,l4 = st.columns(4)

    with l1:
        st.markdown(f'<div class="box blue">LTF FVG<br>{ltf_fvg}</div>', unsafe_allow_html=True)

    with l2:
        st.markdown(f'<div class="box green">LTF MSS<br>{ltf_mss}</div>', unsafe_allow_html=True)

    with l3:
        st.markdown(f'<div class="box purple">MICRO MSS<br>{ltf_micro}</div>', unsafe_allow_html=True)

    with l4:
        st.markdown(f'<div class="box yellow">DISPLACEMENT<br>{displacement_signal}</div>', unsafe_allow_html=True)

    st.markdown(
        f'<div class="box orange">PD ARRAY<br>{pd_zone}</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f'<div class="box green">AI CONFIDENCE SCORE<br>{score}%</div>',
        unsafe_allow_html=True
    )

    # =====================================================
    # LIVE TRADE PANEL
    # =====================================================

    st.subheader("LIVE TRADE PANEL")

    if valid_trade:

        if bias == "BULLISH":

            entry = current_price
            sl = round(entry - 20,2)
            tp1 = round(entry + 40,2)

        else:

            entry = current_price
            sl = round(entry + 20,2)
            tp1 = round(entry - 40,2)

        profit = round(abs(tp1 - entry),2)

        trade_date = datetime.now().strftime("%d-%m-%Y")
        trade_time = datetime.now().strftime("%H:%M:%S")

        big_box = f"""
        <div style="
        background:linear-gradient(135deg,#141e30,#243b55);
        padding:35px;
        border-radius:20px;
        border:2px solid #00c6ff;
        margin-bottom:25px;
        ">

        <h1 style="
        color:#00c6ff;
        text-align:center;
        margin-bottom:30px;
        ">
        SMART MONEY LIVE TRADE
        </h1>

        <div style="
        display:grid;
        grid-template-columns:repeat(3,1fr);
        gap:20px;
        ">

        <div class="box blue">
        DATE<br><br>
        {trade_date}
        </div>

        <div class="box purple">
        TIME<br><br>
        {trade_time}
        </div>

        <div class="box green">
        PAIR<br><br>
        {pair}
        </div>

        <div class="box yellow">
        SESSION<br><br>
        {session}
        </div>

        <div class="box blue">
        ENTRY<br><br>
        {entry}
        </div>

        <div class="box red">
        STOP LOSS<br><br>
        {sl}
        </div>

        <div class="box green">
        TAKE PROFIT<br><br>
        {tp1}
        </div>

        <div class="box purple">
        AI CONFIDENCE<br><br>
        {score}%
        </div>

        <div class="box orange">
        EST PROFIT<br><br>
        {profit}
        </div>

        </div>

        </div>
        """

        st.markdown(
            big_box,
            unsafe_allow_html=True
        )

    else:

        st.warning("NO VALID HTF + LTF SMART MONEY ENTRY")

else:

    st.error("DATA NOT LOADED")