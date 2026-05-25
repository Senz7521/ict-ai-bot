# =========================================================
# ICT AI BOT PRO MAX ULTRA
# FINAL A TO Z VERSION
# STRICT SMART MONEY MODEL
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
# LOAD DATA
# =========================================================

htf_4h = get_data(symbol,"4h")
htf_1h = get_data(symbol,"1h")
ltf_df = get_data(symbol,ltf_timeframe)

# =========================================================
# LIVE PRICE
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
# HTF
# =========================================================

htf_poi = order_block(htf_4h,bias)
htf_fvg = detect_fvg(htf_4h,bias)

htf_poi_tap = False

if bias == "BULLISH":

    if ltf_df["low"].iloc[-1] <= htf_4h["low"].iloc[-5]:
        htf_poi_tap = True

elif bias == "BEARISH":

    if ltf_df["high"].iloc[-1] >= htf_4h["high"].iloc[-5]:
        htf_poi_tap = True

# =========================================================
# LTF
# =========================================================

ltf_mss = detect_mss(ltf_df,bias)

ltf_poi = order_block(ltf_df,bias)

ltf_poi_tap = False

if bias == "BULLISH":

    if ltf_df["low"].iloc[-1] <= ltf_df["low"].iloc[-5]:
        ltf_poi_tap = True

elif bias == "BEARISH":

    if ltf_df["high"].iloc[-1] >= ltf_df["high"].iloc[-5]:
        ltf_poi_tap = True

ltf_micro = micro_mss(ltf_df,bias)

micro_poi = order_block(ltf_df.tail(20),bias)

micro_fvg = detect_fvg(ltf_df.tail(20),bias)

# =========================================================
# AI SCORE
# =========================================================

score = 0

if bias != "NEUTRAL":
    score += 20

if "OB" in str(htf_poi):
    score += 10

if htf_poi_tap:
    score += 10

if "MSS" in ltf_mss:
    score += 20

if "OB" in str(ltf_poi):
    score += 10

if ltf_poi_tap:
    score += 10

if "MICRO" in ltf_micro:
    score += 10

if (
    "OB" in str(micro_poi)
    or
    "FVG" in str(micro_fvg)
):
    score += 10

# =========================================================
# STRICT ENTRY
# =========================================================

valid_trade = False

if (
    bias != "NEUTRAL"
    and "OB" in str(htf_poi)
    and htf_poi_tap == True
    and "MSS" in ltf_mss
    and "OB" in str(ltf_poi)
    and ltf_poi_tap == True
    and "MICRO" in ltf_micro
    and (
        "OB" in str(micro_poi)
        or
        "FVG" in str(micro_fvg)
    )
    and score >= 80
):

    valid_trade = True

# =========================================================
# TOP BOXES
# =========================================================

t1,t2,t3,t4 = st.columns(4)

with t1:
    st.markdown(f'<div class="box blue">PAIR<br><br>{pair}</div>', unsafe_allow_html=True)

with t2:
    st.markdown(f'<div class="box green">LIVE PRICE<br><br>{current_price}</div>', unsafe_allow_html=True)

with t3:
    st.markdown(f'<div class="box purple">SESSION<br><br>{session}</div>', unsafe_allow_html=True)

with t4:
    st.markdown(f'<div class="box orange">LIVE TIME<br><br>{datetime.now().strftime("%H:%M:%S")}</div>', unsafe_allow_html=True)

# =========================================================
# SESSION BOXES
# =========================================================

st.subheader("MARKET SESSIONS")

s1,s2,s3 = st.columns(3)

with s1:
    st.markdown('<div class="box blue">TOKYO SESSION<br><br>5 AM - 12 PM IST</div>', unsafe_allow_html=True)

with s2:
    st.markdown('<div class="box green">LONDON SESSION<br><br>12 PM - 5 PM IST</div>', unsafe_allow_html=True)

with s3:
    st.markdown('<div class="box red">NEW YORK SESSION<br><br>5 PM - 10 PM IST</div>', unsafe_allow_html=True)

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
        close=ltf_df["close"],
        increasing_line_color="#00ff88",
        decreasing_line_color="#ff3355"
    )
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
# HTF + LTF SMART MONEY FLOW
# =========================================================

st.subheader("HTF ANALYSIS")

# =========================================================
# HTF POI
# =========================================================

htf_poi = order_block(htf_4h,bias)

htf_fvg = detect_fvg(htf_4h,bias)

# =========================================================
# HTF TAP
# =========================================================

htf_tap = "NO TAP"

if bias == "BULLISH":

    if ltf_df["low"].iloc[-1] <= htf_4h["low"].iloc[-5]:

        htf_tap = "VALID TAP"

elif bias == "BEARISH":

    if ltf_df["high"].iloc[-1] >= htf_4h["high"].iloc[-5]:

        htf_tap = "VALID TAP"

# =========================================================
# HTF BOXES
# =========================================================

h1,h2,h3,h4,h5 = st.columns(5)

with h1:

    st.markdown(
        f'''
        <div class="box green">
        4H BIAS<br><br>
        {bias_4h}
        </div>
        ''',
        unsafe_allow_html=True
    )

with h2:

    st.markdown(
        f'''
        <div class="box blue">
        1H BIAS<br><br>
        {bias_1h}
        </div>
        ''',
        unsafe_allow_html=True
    )

with h3:

    st.markdown(
        f'''
        <div class="box purple">
        FINAL BIAS<br><br>
        {bias}
        </div>
        ''',
        unsafe_allow_html=True
    )

with h4:

    st.markdown(
        f'''
        <div class="box yellow">
        HTF POI<br><br>
        {htf_poi}
        </div>
        ''',
        unsafe_allow_html=True
    )

with h5:

    st.markdown(
        f'''
        <div class="box orange">
        HTF TAP<br><br>
        {htf_tap}
        </div>
        ''',
        unsafe_allow_html=True
    )

# =========================================================
# LTF ANALYSIS
# =========================================================

st.subheader("LTF ANALYSIS")

# =========================================================
# LTF SWEEP
# =========================================================

ltf_sweep = "NO SWEEP"

prev_high = ltf_df["high"].iloc[-3]

prev_low = ltf_df["low"].iloc[-3]

current_high = ltf_df["high"].iloc[-1]

current_low = ltf_df["low"].iloc[-1]

current_close = ltf_df["close"].iloc[-1]

if current_high > prev_high:

    if current_close < prev_high:

        ltf_sweep = "BUY SIDE SWEEP"

if current_low < prev_low:

    if current_close > prev_low:

        ltf_sweep = "SELL SIDE SWEEP"

# =========================================================
# LTF MSS
# =========================================================

ltf_mss = detect_mss(ltf_df,bias)

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

l1,l2,l3,l4,l5 = st.columns(5)

with l1:

    st.markdown(
        f'''
        <div class="box blue">
        LTF SWEEP<br><br>
        {ltf_sweep}
        </div>
        ''',
        unsafe_allow_html=True
    )

with l2:

    st.markdown(
        f'''
        <div class="box green">
        LTF MSS<br><br>
        {ltf_mss}
        </div>
        ''',
        unsafe_allow_html=True
    )

with l3:

    st.markdown(
        f'''
        <div class="box purple">
        DISPLACEMENT<br><br>
        {ltf_displacement}
        </div>
        ''',
        unsafe_allow_html=True
    )

with l4:

    st.markdown(
        f'''
        <div class="box yellow">
        MICRO POI<br><br>
        {micro_poi}
        </div>
        ''',
        unsafe_allow_html=True
    )

with l5:

    st.markdown(
        f'''
        <div class="box orange">
        MICRO TAP<br><br>
        {micro_tap}
        </div>
        ''',
        unsafe_allow_html=True
    )

# =========================================================
# MICRO FVG BOX
# =========================================================

st.markdown(
    f'''
    <div class="box red">
    MICRO FVG<br><br>
    {micro_fvg}
    </div>
    ''',
    unsafe_allow_html=True
)

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
# AI CONFIDENCE
# =========================================================

st.markdown(
    f'''
    <div class="box green">
    AI CONFIDENCE SCORE<br><br>
    {score}%
    </div>
    ''',
    unsafe_allow_html=True
)

# =========================================================
# FINAL ENTRY MODELS
# =========================================================

retracement_model = False

continuation_model = False

# =========================================================
# MODEL 1
# HTF RETRACEMENT MODEL
# =========================================================

if (

    bias != "NEUTRAL"

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

# =========================================================
# MODEL 2
# CONTINUATION MODEL
# =========================================================

if (

    bias != "NEUTRAL"

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

# =========================================================
# FINAL TRADE VALIDATION
# =========================================================

valid_trade = False

entry_model = "NO VALID ENTRY"

if retracement_model:

    valid_trade = True

    entry_model = "HTF RETRACEMENT MODEL"

elif continuation_model:

    valid_trade = True

    entry_model = "CONTINUATION MODEL"

# =========================================================
# ENTRY MODEL BOX
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

    profit = round(abs(tp1 - entry),2)

    trade_date = datetime.now().strftime("%d-%m-%Y")

    trade_time = datetime.now().strftime("%H:%M:%S")

    st.subheader("LIVE TRADE PANEL")

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

# =========================================================
# TELEGRAM ALERT
# =========================================================

    signal = f"""

ICT AI BOT ALERT

ENTRY MODEL : {entry_model}

PAIR : {pair}

ENTRY : {entry}

SL : {sl}

TP : {tp1}

CONFIDENCE : {score}%

SESSION : {session}

"""

    if st.session_state.last_signal != signal:

        send_telegram(signal)

        st.session_state.last_signal = signal

# =========================================================
# SCORE
# =========================================================

st.markdown(
    f'<div class="box green">AI CONFIDENCE SCORE<br><br>{score}%</div>',
    unsafe_allow_html=True
)

# =========================================================
# SESSION STATE
# =========================================================

if "total_trades" not in st.session_state:
    st.session_state.total_trades = 0

if "wins" not in st.session_state:
    st.session_state.wins = 0

if "losses" not in st.session_state:
    st.session_state.losses = 0

if "trade_history" not in st.session_state:

    st.session_state.trade_history = pd.DataFrame(columns=[
        "DATE",
        "TIME",
        "PAIR",
        "ENTRY",
        "TP",
        "SL",
        "RESULT"
    ])

# =========================================================
# LIVE TRADE PANEL
# =========================================================

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
    {datetime.now().strftime("%d-%m-%Y")}
    </div>

    <div class="box purple">
    TIME<br><br>
    {datetime.now().strftime("%H:%M:%S")}
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
    SL<br><br>
    {sl}
    </div>

    <div class="box green">
    TP<br><br>
    {tp1}
    </div>

    <div class="box purple">
    CONFIDENCE<br><br>
    {score}%
    </div>

    <div class="box orange">
    PROFIT<br><br>
    {profit}
    </div>

    </div>

    </div>
    """

    st.markdown(big_box, unsafe_allow_html=True)

    signal = f"""

ICT AI BOT ALERT

PAIR : {pair}

ENTRY : {entry}

SL : {sl}

TP : {tp1}

CONFIDENCE : {score}%

SESSION : {session}

"""

    if st.session_state.last_signal != signal:

        send_telegram(signal)

        st.session_state.last_signal = signal

else:

    st.warning("NO VALID SMART MONEY ENTRY")

# =========================================================
# DASHBOARD
# =========================================================

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

st.subheader("LIVE TRADING DASHBOARD")

d1,d2,d3,d4 = st.columns(4)

with d1:
    st.markdown(f'<div class="box blue">TOTAL TRADES<br><br>{st.session_state.total_trades}</div>', unsafe_allow_html=True)

with d2:
    st.markdown(f'<div class="box green">TOTAL WINS<br><br>{st.session_state.wins}</div>', unsafe_allow_html=True)

with d3:
    st.markdown(f'<div class="box red">TOTAL LOSSES<br><br>{st.session_state.losses}</div>', unsafe_allow_html=True)

with d4:
    st.markdown(f'<div class="box purple">WIN RATE<br><br>{win_rate}%</div>', unsafe_allow_html=True)

# =========================================================
# LIVE TRADE HISTORY
# =========================================================

st.subheader("LIVE TRADE HISTORY")

st.dataframe(
    st.session_state.trade_history,
    use_container_width=True
)