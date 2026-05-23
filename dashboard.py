import streamlit as st
import ccxt
import pandas as pd

st.set_page_config(page_title="ICT AI BOT", layout="wide")

st.title("ICT AI BOT")

# COIN SELECT
coin = st.selectbox(
    "Select Coin",
    ["BTC/USD", "ETH/USD"]
)

# LOGO
if coin == "BTC/USD":
    st.image(
        "https://cryptologos.cc/logos/bitcoin-btc-logo.png",
        width=100
    )

if coin == "ETH/USD":
    st.image(
        "https://cryptologos.cc/logos/ethereum-eth-logo.png",
        width=100
    )

try:
    # EXCHANGE
    exchange = ccxt.coinbase({
        'enableRateLimit': True
    })

    # LIVE PRICE
    ticker = exchange.fetch_ticker(coin)
    st.markdown("## Market Analysis")
except Exception as e:
    st.error(f"Error: {e}")

st.markdown("## Entry Model")

try:

# =========================
# HTF BIAS
# =========================
# prepare HTF arrays (from previously fetched ohlcv)
    if 'ohlcv' in locals() and ohlcv:
        htf_highs = [c[2] for c in ohlcv]
        htf_lows = [c[3] for c in ohlcv]
        htf_closes = [c[4] for c in ohlcv]

        # use recent 10 candles (exclude last candle)
        recent_htf_high = max(htf_highs[-10:-1]) if len(htf_highs) >= 2 else htf_highs[-1]
        recent_htf_low = min(htf_lows[-10:-1]) if len(htf_lows) >= 2 else htf_lows[-1]
    else:
        # defaults if ohlcv not available
        htf_highs = htf_lows = htf_closes = []
        recent_htf_high = recent_htf_low = 0

    if htf_closes and htf_closes[-1] > recent_htf_high:
        htf_bias = "bullish"
    elif htf_closes and htf_closes[-1] < recent_htf_low:
        htf_bias = "bearish"
    else:
        htf_bias = "range"

    col1, col2 = st.columns(2)

    with col1:
        st.info(f"HTF Bias: {htf_bias}")
        st.info("HTF POI: Premium Zone")
        st.info("LTF POI: Discount Zone")

    with col2:
        st.success("MSS: Bullish MSS")
        st.success("MFVG: Active")
        st.success("ENTRY: BUY")
        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Live Price",
            ticker['last']
        )

        col2.metric(
            "24H High",
            ticker['high']
        )

        col3.metric(
            "24H Low",
            ticker['low']
        )

        # OHLCV DATA
        ohlcv = exchange.fetch_ohlcv(
            coin,
            timeframe='1h',
            limit=50
        )

        df = pd.DataFrame(
            ohlcv,
            columns=[
                'Time',
                'Open',
                'High',
                'Low',
                'Close',
                'Volume'
            ]
        )

        st.dataframe(df)

        st.success("BOT RUNNING SUCCESSFULLY")

except Exception as e:
    st.error(f"Error: {e}")

# =========================
# HTF BIAS
# =========================
# prepare HTF arrays (from previously fetched ohlcv)
if 'ohlcv' in locals() and ohlcv:
    htf_highs = [c[2] for c in ohlcv]
    htf_lows = [c[3] for c in ohlcv]
    htf_closes = [c[4] for c in ohlcv]

    # use recent 10 candles (exclude last candle)
    recent_htf_high = max(htf_highs[-10:-1]) if len(htf_highs) >= 2 else htf_highs[-1]
    recent_htf_low = min(htf_lows[-10:-1]) if len(htf_lows) >= 2 else htf_lows[-1]
else:
    # defaults if ohlcv not available
    htf_highs = htf_lows = htf_closes = []
    recent_htf_high = recent_htf_low = 0


if htf_closes[-1] > recent_htf_high:
    htf_bias = "bullish"

elif htf_closes[-1] < recent_htf_low:
    htf_bias = "bearish"

else:
    htf_bias = "range"

# =========================
# LTF DATA
# =========================

ltf = exchange.fetch_ohlcv(
    'BTC/USD',
    timeframe='1m',
    limit=20
)

ltf_highs = [c[2] for c in ltf]
ltf_lows = [c[3] for c in ltf]
ltf_closes = [c[4] for c in ltf]

recent_ltf_high = max(ltf_highs[-10:-1])
recent_ltf_low = min(ltf_lows[-10:-1])

# =========================
# LTF BIAS
# =========================

if ltf_closes[-1] > recent_ltf_high:
    ltf_bias = "bullish"

elif ltf_closes[-1] < recent_ltf_low:
    ltf_bias = "bearish"

else:
    ltf_bias = "range"

# =========================
# MSS
# =========================

bullish_mss = ltf_closes[-1] > recent_ltf_high
bearish_mss = ltf_closes[-1] < recent_ltf_low

# =========================
# DISPLACEMENT
# =========================

last = ltf[-1]

body = abs(last[4] - last[1])
range_ = last[2] - last[3]

if range_ == 0:
    displacement = 0
else:
    displacement = body / range_

# =========================
# UI
# =========================

st.subheader("Market Analysis")

st.write("HTF Bias:", htf_bias)
st.write("LTF Bias:", ltf_bias)
st.write("Displacement:", round(displacement,2))
# =========================
# ENTRY MODEL
# =========================

st.markdown("## ENTRY MODEL")

col1, col2 = st.columns(2)

# LEFT SIDE
with col1:

    st.info("HTF Bias: Bullish")

    st.info("HTF POI: 4H Bullish Order Block")

    st.info("LTF POI: 15M Discount Zone")

    st.info("Liquidity: SSL Swept")

# RIGHT SIDE
with col2:
    if htf_bias == "bullish" and ltf_bias == "bullish":
        st.success("ENTRY: BUY")
    elif htf_bias == "bearish" and ltf_bias == "bearish":
        st.error("ENTRY: SELL")
    else:
        st.warning("ENTRY: NO TRADE")

# ENTRY SIGNAL
st.markdown("### ENTRY SIGNAL")

entry_col1, entry_col2, entry_col3 = st.columns(3)

with entry_col1:
    st.metric("ENTRY", "BUY")

with entry_col2:
    st.metric("SL", "76500")

with entry_col3:
    st.metric("TP", "78200")

# RR
st.success("Risk Reward: 1 : 3")

# FINAL CONFIRMATION
st.success("ICT SNIPER MODEL CONFIRMED")
# =========================
# SIGNALS
# =========================

if htf_bias == "bullish":

    if bullish_mss and displacement > 0.7:

        st.success("BUY SIGNAL")

    else:

        st.warning("NO BUY SETUP")

elif htf_bias == "bearish":

    if bearish_mss and displacement > 0.7:

        st.error("SELL SIGNAL")

    else:

        st.warning("NO SELL SETUP")

else:

    st.info("RANGE MARKET")
    import streamlit as st

st.title("ICT AI BOT")
st.success("Dashboard Running")
import streamlit as st

st.set_page_config(
    page_title="ICT AI BOT",
    layout="wide"
)

# ===== STYLE =====
st.markdown("""
<style>
body {
    background-color: #0e1117;
}

.main {
    background-color: #0e1117;
    color: white;
}

.big-font {
    font-size:40px !important;
    font-weight: bold;
    color: #00ff99;
}

.signal-buy {
    padding: 20px;
    border-radius: 10px;
    background-color: #002b1f;
    color: #00ff99;
    font-size: 28px;
    font-weight: bold;
    text-align:center;
}

.signal-sell {
    padding: 20px;
    border-radius: 10px;
    background-color: #2b0000;
    color: red;
    font-size: 28px;
    font-weight: bold;
    text-align:center;
}

.info-box {
    padding: 15px;
    border-radius: 10px;
    background-color: #1c1f26;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

# ===== TITLE =====
st.markdown('<p class="big-font">ICT AI BOT</p>', unsafe_allow_html=True)

# ===== MARKET DATA =====
htf_bias = "bullish"
ltf_bias = "bullish"
displacement = 1.2

# ===== INFO =====
st.markdown(f"""
<div class="info-box">
<h3>HTF Bias: {htf_bias}</h3>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="info-box">
<h3>LTF Bias: {ltf_bias}</h3>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="info-box">
<h3>Displacement: {displacement}</h3>
</div>
""", unsafe_allow_html=True)

# ===== SIGNAL =====
if htf_bias == "bullish" and displacement > 0.7:
    st.markdown(
        '<div class="signal-buy">BUY SIGNAL 🚀</div>',
        unsafe_allow_html=True
    )

elif htf_bias == "bearish" and displacement > 0.7:
    st.markdown(
        '<div class="signal-sell">SELL SIGNAL 🔻</div>',
        unsafe_allow_html=True
    )

else:
    st.warning("RANGE MARKET")