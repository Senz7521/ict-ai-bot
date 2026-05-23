import streamlit as st
import ccxt

# =========================
# TITLE
# =========================

st.title("ICT AI BOT")

# =========================
# EXCHANGE
# =========================

exchange = ccxt.binance()

# =========================
# HTF DATA
# =========================

htf = exchange.fetch_ohlcv(
    'BTC/USDT',
    timeframe='4h',
    limit=50
)

htf_highs = [c[2] for c in htf]
htf_lows = [c[3] for c in htf]
htf_closes = [c[4] for c in htf]

recent_htf_high = max(htf_highs[-20:-1])
recent_htf_low = min(htf_lows[-20:-1])

# =========================
# HTF BIAS
# =========================

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
    'BTC/USDT',
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