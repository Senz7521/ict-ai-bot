# =========================================================
# ICT AI BOT PRO MAX ULTRA
# FINAL INSTITUTIONAL VERSION
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
from telegram_pro import *
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



try:

        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

        data = {
            "chat_id": CHAT_ID,
            "text": message
        }

        requests.post(url,data=data)

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
    "XAU/USD":"XAUUSDT"
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

# =========================================================
# DAILY BIAS ENGINE
# =========================================================

def daily_bias(df):

    pdh = df["high"].iloc[-2]

    pdl = df["low"].iloc[-2]

    current = df["close"].iloc[-1]

    if current > pdh:
        return "BULLISH DAILY FLOW"

    elif current < pdl:
        return "BEARISH DAILY FLOW"

    return "RANGING DAILY FLOW"

# =========================================================
# PREMIUM / DISCOUNT
# =========================================================

def premium_discount(df):

    high = df["high"].iloc[-50:].max()

    low = df["low"].iloc[-50:].min()

    eq = (high + low) / 2

    current = df["close"].iloc[-1]

    if current > eq:
        return "PREMIUM"

    return "DISCOUNT"

# =========================================================
# NEWS FILTER
# =========================================================

def news_filter():

    hour = datetime.now().hour

    if hour == 18:
        return "HIGH IMPACT NEWS"

    return "SAFE"

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

    return "NO SESSION"

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
                and
                df["close"].iloc[i+1] > df["high"].iloc[i]
            ):

                return "BULLISH OB"

        elif bias == "BEARISH":

            if (
                df["close"].iloc[i] > df["open"].iloc[i]
                and
                df["close"].iloc[i+1] < df["low"].iloc[i]
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
# REAL MSS
# =========================================================

def detect_mss(df,bias):

    high1 = df["high"].iloc[-5]

    high2 = df["high"].iloc[-3]

    low1 = df["low"].iloc[-5]

    low2 = df["low"].iloc[-3]

    close = df["close"].iloc[-1]

    if bias == "BULLISH":

        if high2 > high1 and close > high2:
            return "BULLISH MSS"

    elif bias == "BEARISH":

        if low2 < low1 and close < low2:
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
# LOAD DATA
# =========================================================

htf_4h = get_data(symbol,"4h")
htf_1h = get_data(symbol,"1h")
ltf_df = get_data(symbol,ltf_timeframe)

# =========================================================
# PRICE
# =========================================================

current_price = round(
    float(ltf_df["close"].iloc[-1]),
    2
)

# =========================================================
# SESSION
# =========================================================

session = session_filter()

# =========================================================
# BIAS
# =========================================================

bias_4h = get_htf_bias(htf_4h)
bias_1h = get_htf_bias(htf_1h)

if bias_4h == bias_1h:
    bias = bias_4h
else:
    bias = "NEUTRAL"

# =========================================================
# DAILY FLOW / PD / NEWS
# =========================================================

daily_flow = daily_bias(htf_4h)

pd_zone = premium_discount(htf_4h)

news_status = news_filter()

# =========================================================
# HTF
# =========================================================

htf_poi = order_block(htf_4h,bias)

htf_fvg = detect_fvg(htf_4h,bias)

htf_tap = "NO TAP"

if bias == "BULLISH":

    if ltf_df["low"].iloc[-1] <= htf_4h["low"].iloc[-5]:

        htf_tap = "VALID TAP"

elif bias == "BEARISH":

    if ltf_df["high"].iloc[-1] >= htf_4h["high"].iloc[-5]:

        htf_tap = "VALID TAP"

# =========================================================
# LTF
# =========================================================

ltf_mss = detect_mss(ltf_df,bias)

ltf_sweep = "NO SWEEP"

prev_high = ltf_df["high"].iloc[-3]
prev_low = ltf_df["low"].iloc[-3]

current_high = ltf_df["high"].iloc[-1]
current_low = ltf_df["low"].iloc[-1]

if current_high > prev_high:

    if current_price < prev_high:

        ltf_sweep = "BUY SIDE SWEEP"

if current_low < prev_low:

    if current_price > prev_low:

        ltf_sweep = "SELL SIDE SWEEP"

ltf_displacement = "NO DISPLACEMENT"

candle_range = (
    ltf_df["high"].iloc[-1]
    -
    ltf_df["low"].iloc[-1]
)

avg_range = (
    (
        ltf_df["high"]
        -
        ltf_df["low"]
    )
    .rolling(10)
    .mean()
    .iloc[-1]
)

if candle_range > avg_range * 1.5:

    ltf_displacement = "VALID DISPLACEMENT"

micro_poi = order_block(
    ltf_df.tail(20),
    bias
)

micro_fvg = detect_fvg(
    ltf_df.tail(20),
    bias
)

micro_signal = micro_mss(
    ltf_df,
    bias
)

micro_tap = "NO TAP"

if bias == "BULLISH":

    if ltf_df["low"].iloc[-1] <= ltf_df["low"].iloc[-2]:

        micro_tap = "VALID TAP"

elif bias == "BEARISH":

    if ltf_df["high"].iloc[-1] >= ltf_df["high"].iloc[-2]:

        micro_tap = "VALID TAP"

# =========================================================
# AI SCORE
# =========================================================

score = 0

if bias != "NEUTRAL":
    score += 15

if htf_tap == "VALID TAP":
    score += 15

if "SWEEP" in ltf_sweep:
    score += 15

if "MSS" in ltf_mss:
    score += 15

if "VALID" in ltf_displacement:
    score += 15

if "OB" in str(micro_poi):
    score += 10

if "FVG" in str(micro_fvg):
    score += 10

if micro_tap == "VALID TAP":
    score += 5

# =========================================================
# ENTRY QUALITY
# =========================================================

quality = "C"

if score >= 90:
    quality = "A+"

elif score >= 80:
    quality = "A"

elif score >= 70:
    quality = "B"

# =========================================================
# ENTRY MODELS
# =========================================================

retracement_model = False
continuation_model = False

if (

    bias != "NEUTRAL"

    and

    news_status == "SAFE"

    and

    (
        (bias == "BULLISH" and pd_zone == "DISCOUNT")
        or
        (bias == "BEARISH" and pd_zone == "PREMIUM")
    )

    and

    (
        "OB" in str(htf_poi)
        or
        "FVG" in str(htf_fvg)
    )

    and

    htf_tap == "VALID TAP"

    and

    "SWEEP" in ltf_sweep

    and

    "MSS" in ltf_mss

    and

    "VALID" in ltf_displacement

    and

    (
        "OB" in str(micro_poi)
        or
        "FVG" in str(micro_fvg)
    )

    and

    micro_tap == "VALID TAP"

):

    retracement_model = True

if (

    bias != "NEUTRAL"

    and

    news_status == "SAFE"

    and

    "MSS" in ltf_mss

    and

    "VALID" in ltf_displacement

    and

    (
        "OB" in str(micro_poi)
        or
        "FVG" in str(micro_fvg)
    )

    and

    session != "NO SESSION"

):

    continuation_model = True

valid_trade = False

entry_model = "NO VALID ENTRY"

if retracement_model:

    valid_trade = True
    entry_model = "HTF RETRACEMENT MODEL"

elif continuation_model:

    valid_trade = True
    entry_model = "CONTINUATION MODEL"

# =========================================================
# TOP BOXES
# =========================================================

t1,t2,t3,t4 = st.columns(4)

with t1:
    st.markdown(f'<div class="box blue">PAIR<br><br>{pair}</div>',unsafe_allow_html=True)

with t2:
    st.markdown(f'<div class="box green">LIVE PRICE<br><br>{current_price}</div>',unsafe_allow_html=True)

with t3:
    st.markdown(f'<div class="box purple">SESSION<br><br>{session}</div>',unsafe_allow_html=True)

with t4:
    st.markdown(f'<div class="box orange">LIVE TIME<br><br>{datetime.now().strftime("%H:%M:%S")}</div>',unsafe_allow_html=True)

# =========================================================
# CHART
# =========================================================

st.subheader("LIVE SMART MONEY CHART")

fig = go.Figure()

fig.add_trace(
    go.Candlestick(
        x=ltf_df["time"],
        open=ltf_df["open"],
        high=ltf_df["high"],
        low=ltf_df["low"],
        close=ltf_df["close"]
    )
)

fig.add_hline(
    y=current_price,
    line_dash="dot",
    line_color="yellow"
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
# HTF ANALYSIS
# =========================================================

st.subheader("HTF ANALYSIS")

h1,h2,h3,h4,h5 = st.columns(5)

with h1:
    st.markdown(f'<div class="box green">4H BIAS<br><br>{bias_4h}</div>',unsafe_allow_html=True)

with h2:
    st.markdown(f'<div class="box blue">1H BIAS<br><br>{bias_1h}</div>',unsafe_allow_html=True)

with h3:
    st.markdown(f'<div class="box purple">FINAL BIAS<br><br>{bias}</div>',unsafe_allow_html=True)

with h4:
    st.markdown(f'<div class="box yellow">HTF POI<br><br>{htf_poi}</div>',unsafe_allow_html=True)

with h5:
    st.markdown(f'<div class="box orange">HTF TAP<br><br>{htf_tap}</div>',unsafe_allow_html=True)

st.markdown(f'<div class="box blue">DAILY FLOW<br><br>{daily_flow}</div>',unsafe_allow_html=True)

st.markdown(f'<div class="box purple">PD ARRAY<br><br>{pd_zone}</div>',unsafe_allow_html=True)

st.markdown(f'<div class="box red">NEWS FILTER<br><br>{news_status}</div>',unsafe_allow_html=True)

# =========================================================
# LTF ANALYSIS
# =========================================================

st.subheader("LTF ANALYSIS")

# =========================================================
# LTF BIAS
# =========================================================

ltf_bias = "NEUTRAL"

if bias == "BULLISH":

    if current_price > ltf_df["close"].iloc[-5]:

        ltf_bias = "BULLISH"

elif bias == "BEARISH":

    if current_price < ltf_df["close"].iloc[-5]:

        ltf_bias = "BEARISH"

# =========================================================
# LTF POI
# =========================================================

ltf_poi = order_block(
    ltf_df,
    bias
)

ltf_fvg = detect_fvg(
    ltf_df,
    bias
)

ltf_poi_box = "NO POI"

if "OB" in str(ltf_poi):

    ltf_poi_box = ltf_poi

elif "FVG" in str(ltf_fvg):

    ltf_poi_box = ltf_fvg

# =========================================================
# LTF POI TAP
# =========================================================

ltf_poi_tap = "NO TAP"

if bias == "BULLISH":

    if ltf_df["low"].iloc[-1] <= ltf_df["low"].iloc[-3]:

        ltf_poi_tap = "VALID TAP"

elif bias == "BEARISH":

    if ltf_df["high"].iloc[-1] >= ltf_df["high"].iloc[-3]:

        ltf_poi_tap = "VALID TAP"

# =========================================================
# LTF DISPLACEMENT
# =========================================================

ltf_displacement = "NO DISPLACEMENT"

candle_range = (
    ltf_df["high"].iloc[-1]
    -
    ltf_df["low"].iloc[-1]
)

avg_range = (
    (
        ltf_df["high"]
        -
        ltf_df["low"]
    )
    .rolling(10)
    .mean()
    .iloc[-1]
)

if candle_range > avg_range * 1.5:

    ltf_displacement = "VALID DISPLACEMENT"

# =========================================================
# LTF MSS
# =========================================================

ltf_mss = detect_mss(
    ltf_df,
    bias
)

# =========================================================
# MICRO POI
# =========================================================

micro_poi = order_block(
    ltf_df.tail(20),
    bias
)

micro_fvg = detect_fvg(
    ltf_df.tail(20),
    bias
)

micro_box = "NO MICRO POI"

if "OB" in str(micro_poi):

    micro_box = micro_poi

elif "FVG" in str(micro_fvg):

    micro_box = micro_fvg

# =========================================================
# MICRO TAP
# =========================================================

micro_tap = "NO TAP"

if bias == "BULLISH":

    if ltf_df["low"].iloc[-1] <= ltf_df["low"].iloc[-2]:

        micro_tap = "VALID TAP"

elif bias == "BEARISH":

    if ltf_df["high"].iloc[-1] >= ltf_df["high"].iloc[-2]:

        micro_tap = "VALID TAP"

# =========================================================
# LTF BOXES
# =========================================================

l1,l2,l3,l4,l5,l6 = st.columns(6)

with l1:

    st.markdown(
        f'''
        <div class="box blue">
        LTF BIAS<br><br>
        {ltf_bias}
        </div>
        ''',
        unsafe_allow_html=True
    )

with l2:

    st.markdown(
        f'''
        <div class="box green">
        LTF POI<br><br>
        {ltf_poi_box}
        </div>
        ''',
        unsafe_allow_html=True
    )

with l3:

    st.markdown(
        f'''
        <div class="box yellow">
        LTF POI TAP<br><br>
        {ltf_poi_tap}
        </div>
        ''',
        unsafe_allow_html=True
    )

with l4:

    st.markdown(
        f'''
        <div class="box purple">
        DISPLACEMENT<br><br>
        {ltf_displacement}
        </div>
        ''',
        unsafe_allow_html=True
    )

with l5:

    st.markdown(
        f'''
        <div class="box orange">
        LTF MSS<br><br>
        {ltf_mss}
        </div>
        ''',
        unsafe_allow_html=True
    )

with l6:

    st.markdown(
        f'''
        <div class="box red">
        MICRO POI<br><br>
        {micro_box}
        </div>
        ''',
        unsafe_allow_html=True
    )

# =========================================================
# MICRO TAP BOX
# =========================================================

st.markdown(
    f'''
    <div class="box green">
    MICRO TAP<br><br>
    {micro_tap}
    </div>
    ''',
    unsafe_allow_html=True
)

# =========================================================
# ENTRY MODEL
# =========================================================

st.subheader("ENTRY MODEL")

if valid_trade:

    st.markdown(
        f'''
        <div class="box green">
        {entry_model}
        </div>
        ''',
        unsafe_allow_html=True
    )

else:

    st.markdown(
        '''
        <div class="box red">
        NO VALID SMART MONEY ENTRY
        </div>
        ''',
        unsafe_allow_html=True
    )

# =========================================================
# LIVE TRADE PANEL
# =========================================================

if valid_trade:

    if bias == "BULLISH":

        entry = current_price
        sl = round(entry - 20,2)
        tp1 = round(entry + 40,2)

    else:

        entry = current_price
        sl = round(entry + 20,2)
        tp1 = round(entry - 40,2)

    st.subheader("LIVE TRADE PANEL")

    live_box = f"""
    <div style="
    background:linear-gradient(135deg,#141e30,#243b55);
    padding:35px;
    border-radius:20px;
    border:2px solid #00c6ff;
    margin-bottom:25px;
    ">

    <div style="
    display:grid;
    grid-template-columns:repeat(4,1fr);
    gap:20px;
    ">

    <div class="box blue">
    DATE<br><br>
    {datetime.now().strftime("%d-%m-%Y")}
    </div>

    <div class="box purple">
    TIME<br><br>
    {datetime.now().strftime("%H:%M:%S")}
    </div>

    <div class="box green">
    SESSION<br><br>
    {session}
    </div>

    <div class="box orange">
    PAIR<br><br>
    {pair}
    </div>

    <div class="box blue">
    ENTRY<br><br>
    {entry}
    </div>

    <div class="box red">
    SL<br><br>
    {sl}
    </div>

    <div class="box green">
    TP<br><br>
    {tp1}
    </div>

    <div class="box purple">
    ENTRY MODEL<br><br>
    {entry_model}
    </div>

    </div>

    </div>
    """

    st.markdown(
        live_box,
        unsafe_allow_html=True
    )

else:

    st.warning("NO VALID SMART MONEY ENTRY")

# =========================================================
# DASHBOARD
# =========================================================

if "total_trades" not in st.session_state:
    st.session_state.total_trades = 0

if "wins" not in st.session_state:
    st.session_state.wins = 0

if "losses" not in st.session_state:
    st.session_state.losses = 0

win_rate = 0

if st.session_state.total_trades > 0:

    win_rate = round(
        (
            st.session_state.wins
            /
            st.session_state.total_trades
        ) * 100,
        2
    )

st.subheader("BACKTEST RESULTS")
# =========================================================
# TRADE HISTORY
# =========================================================

if "trade_history" not in st.session_state:

    st.session_state.trade_history = pd.DataFrame(columns=[

        "DATE",
        "TIME",
        "SESSION",
        "PAIR",
        "ENTRY",
        "TP",
        "SL",
        "MODEL"

    ])

# =========================================================
# SAVE TRADE
# =========================================================

if valid_trade:

    new_trade = {

        "DATE": datetime.now().strftime("%d-%m-%Y"),

        "TIME": datetime.now().strftime("%H:%M:%S"),

        "SESSION": session,

        "PAIR": pair,

        "ENTRY": entry,

        "TP": tp1,

        "SL": sl,

        "MODEL": entry_model

    }

    latest = pd.DataFrame([new_trade])

    if st.session_state.trade_history.empty:

        st.session_state.trade_history = latest

    else:

        last_entry = st.session_state.trade_history.iloc[-1]

        if (
            last_entry["ENTRY"] != entry
            or
            last_entry["PAIR"] != pair
        ):

            st.session_state.trade_history = pd.concat(

                [
                    latest,
                    st.session_state.trade_history
                ],

                ignore_index=True

            )

# =========================================================
# SHOW HISTORY
# =========================================================

st.subheader("LIVE TRADE HISTORY")

st.dataframe(

    st.session_state.trade_history,

    use_container_width=True

)
b1,b2,b3 = st.columns(3)

with b1:
    st.markdown(f'<div class="box blue">WIN RATE<br><br>{win_rate}%</div>',unsafe_allow_html=True)

with b2:
    st.markdown('<div class="box green">RISK REWARD<br><br>1:2</div>',unsafe_allow_html=True)

with b3:

    pnl = (
        st.session_state.wins * 40
        -
        st.session_state.losses * 20
    )

    st.markdown(f'<div class="box purple">EST PNL<br><br>{pnl}</div>',unsafe_allow_html=True)