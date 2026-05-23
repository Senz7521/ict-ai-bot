import ccxt
import requests

# =========================
# TELEGRAM CONFIG
# =========================

TOKEN = "8724361307:AAHD9f1bQUgzvUr3eW-0TfgpN1eGhNNUaTc"
CHAT_ID = "7790207379"

def send_telegram(msg):

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": msg
    }

    requests.post(url, data=data)

# =========================
# EXCHANGE
# =========================

exchange = ccxt.binance()

# =========================
# HTF DATA (4H)
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

print("HTF Bias:", htf_bias)

# =========================
# HTF POI (5M)
# =========================

poi = exchange.fetch_ohlcv(
    'BTC/USDT',
    timeframe='5m',
    limit=30
)

bullish_ob = False
bearish_ob = False

for candle in poi:

    open_ = candle[1]
    close_ = candle[4]

    # Bullish OB
    if close_ < open_:
        bullish_ob = True

    # Bearish OB
    if close_ > open_:
        bearish_ob = True

# =========================
# HTF FVG
# =========================

c1_high = poi[-3][2]
c1_low = poi[-3][3]

c3_high = poi[-1][2]
c3_low = poi[-1][3]

bullish_fvg = c1_high < c3_low
bearish_fvg = c1_low > c3_high

print("Bullish FVG:", bullish_fvg)
print("Bearish FVG:", bearish_fvg)

# =========================
# LTF DATA (1M)
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

print("LTF Bias:", ltf_bias)

# =========================
# MSS
# =========================

bullish_mss = ltf_closes[-1] > recent_ltf_high
bearish_mss = ltf_closes[-1] < recent_ltf_low

print("Bullish MSS:", bullish_mss)
print("Bearish MSS:", bearish_mss)

# =========================
# DISPLACEMENT
# =========================

last = ltf[-1]

open_price = last[1]
high_price = last[2]
low_price = last[3]
close_price = last[4]

body = abs(close_price - open_price)
range_ = high_price - low_price

if range_ == 0:
    displacement = 0
else:
    displacement = body / range_

print("Displacement:", displacement)

# =========================
# BUY LOGIC
# =========================

if htf_bias == "bullish":

    if bullish_ob or bullish_fvg:

        if ltf_bias == "bullish":

            if bullish_mss:

                if displacement > 0.7:

                    signal = f'''
BTCUSDT BUY SIGNAL

HTF Bias: Bullish
HTF POI: Bullish

LTF Bias: Bullish
MSS: Confirmed

Displacement: {round(displacement,2)}

ENTRY: {close_price}
SL: {low_price}
TP: External Liquidity
RR: 1:3
'''

                    print(signal)

                    send_telegram(signal)

                else:
                    print("No Buy - Weak Displacement")

            else:
                print("No Buy - MSS Missing")

        else:
            print("No Buy - LTF Bearish")

    else:
        print("No Buy - No Bullish POI")

# =========================
# SELL LOGIC
# =========================

elif htf_bias == "bearish":

    if bearish_ob or bearish_fvg:

        if ltf_bias == "bearish":

            if bearish_mss:

                if displacement > 0.7:

                    signal = f'''
BTCUSDT SELL SIGNAL

HTF Bias: Bearish
HTF POI: Bearish

LTF Bias: Bearish
MSS: Confirmed

Displacement: {round(displacement,2)}

ENTRY: {close_price}
SL: {high_price}
TP: External Liquidity
RR: 1:3
'''

                    print(signal)

                    send_telegram(signal)

                else:
                    print("No Sell - Weak Displacement")

            else:
                print("No Sell - MSS Missing")

        else:
            print("No Sell - LTF Bullish")

    else:
        print("No Sell - No Bearish POI")

else:
    print("No Trade - Range Market")