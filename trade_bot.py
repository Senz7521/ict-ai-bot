import ccxt
import pandas as pd
import time

# =========================
# EXCHANGE
# =========================

exchange = ccxt.bybit()

SYMBOL = "BTC/USDT"
TIMEFRAME = "1m"

# =========================
# LOOP
# =========================

while True:

    # FETCH DATA
    ohlcv = exchange.fetch_ohlcv(SYMBOL, TIMEFRAME, limit=200)

    # DATAFRAME
    df = pd.DataFrame(
        ohlcv,
        columns=["time","open","high","low","close","volume"]
    )

    # =========================
    # LAST VALUES
    # =========================

    close = df["close"]
    high = df["high"]
    low = df["low"]

    last_close = close.iloc[-1]
    prev_close = close.iloc[-2]

    last_high = high.iloc[-1]
    prev_high = high.iloc[-2]

    last_low = low.iloc[-1]
    prev_low = low.iloc[-2]

    # =========================
    # HTF BIAS
    # =========================

    if last_close > close.iloc[-20]:
        htf_bias = "BULLISH"
    else:
        htf_bias = "BEARISH"

    # =========================
    # HTF POI
    # =========================

    if htf_bias == "BULLISH":
        htf_poi = low.iloc[-10]
    else:
        htf_poi = high.iloc[-10]

    # =========================
    # POI TAP
    # =========================

    poi_tap = False

    if htf_bias == "BULLISH":
        if last_low <= htf_poi:
            poi_tap = True

    if htf_bias == "BEARISH":
        if last_high >= htf_poi:
            poi_tap = True

    # =========================
    # LTF MSS
    # =========================

    ltf_mss = False

    if htf_bias == "BULLISH":
        if last_high > prev_high:
            ltf_mss = True

    if htf_bias == "BEARISH":
        if last_low < prev_low:
            ltf_mss = True

    # =========================
    # MICRO MSS
    # =========================

    micro_mss = False

    if htf_bias == "BULLISH":
        if close.iloc[-1] > close.iloc[-2]:
            micro_mss = True

    if htf_bias == "BEARISH":
        if close.iloc[-1] < close.iloc[-2]:
            micro_mss = True

    # =========================
    # ENTRY
    # =========================

    entry = "NO ENTRY"

sl = 0
tp = 0

# BUY ENTRY
if (
    htf_bias == "BULLISH"
    and poi_tap
    and ltf_mss
    and micro_mss
):

    entry = "BUY"

    entry_price = last_close

    sl = entry_price - 5
    tp = entry_price + 15

# SELL ENTRY
if (
    htf_bias == "BEARISH"
    and poi_tap
    and ltf_mss
    and micro_mss
):

    entry = "SELL"

    entry_price = last_close

    sl = entry_price + 5
    tp = entry_price - 15

    if (
        htf_bias == "BULLISH"
        and poi_tap
        and ltf_mss
        and micro_mss
    ):
        entry = "BUY"

    if (
        htf_bias == "BEARISH"
        and poi_tap
        and ltf_mss
        and micro_mss
    ):
        entry = "SELL"

    # =========================
    # OUTPUT
    # =========================

    print("\n==========================")
    print("ICT AI BOT")
    print("==========================")

    print("PAIR:", SYMBOL)
    print("HTF BIAS:", htf_bias)
    print("HTF POI:", round(htf_poi, 2))
    print("POI TAP:", poi_tap)
    print("LTF MSS:", ltf_mss)
    print("MICRO MSS:", micro_mss)
    print("ENTRY:", entry)

    print("==========================")

    # =========================
    # WAIT
    # =========================

    time.sleep(10)