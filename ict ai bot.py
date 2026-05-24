# =========================================================
# ICT AI BOT PRO FINAL FIXED VERSION
# BYBIT + TELEGRAM + ICT LOGIC
# =========================================================

# =========================================================
# IMPORTS
# =========================================================

import ccxt
import pandas as pd
import time
import requests
from datetime import datetime

# =========================================================
# TELEGRAM SETTINGS
# =========================================================

TOKEN = "8910102188:AAFAQGQKjIOUMB19HHYSQKC4-0fKly3ASxE"
CHAT_ID = "7790207379"

def send_telegram(msg):

    try:

        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

        data = {
            "chat_id": CHAT_ID,
            "text": msg
        }

        requests.post(url, data=data)

    except Exception as e:

        print("TELEGRAM ERROR:", e)

# =========================================================
# EXCHANGE
# =========================================================

exchange = ccxt.bybit({
    "enableRateLimit": True,
    "options": {
        "defaultType": "future"
    }
})

# =========================================================
# SYMBOLS
# =========================================================

SYMBOLS = [
    "BTC/USDT",
    "ETH/USDT",
    "XRP/USDT"
]

# =========================================================
# FETCH CANDLES
# =========================================================

def get_candles(symbol, timeframe="1m", limit=200):

    try:

        ohlcv = exchange.fetch_ohlcv(
            symbol=symbol,
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

        df["ema_200"] = df["close"].ewm(span=200).mean()

        return df

    except Exception as e:

        print("CANDLE ERROR:", e)

        return None

# =========================================================
# SESSION FILTER
# =========================================================

def session_filter():

    utc_hour = datetime.utcnow().hour

    if 7 <= utc_hour <= 11:
        return "LONDON SESSION"

    elif 12 <= utc_hour <= 16:
        return "NEW YORK SESSION"

    else:
        return "ASIAN / DEAD SESSION"

# =========================================================
# HTF BIAS
# =========================================================

def get_htf_bias(df):

    def get_htf_bias(df):

        last_high = df["high"].iloc[-2]
        old_high = df["high"].iloc[-10]

        last_low = df["low"].iloc[-2]
        old_low = df["low"].iloc[-10]

        # Bullish Structure
        if last_high > old_high:
            return "BULLISH"

        # Bearish Structure
        elif last_low < old_low:
            return "BEARISH"

        return "NEUTRAL"

# =========================================================
# ORDER BLOCK / POI
# =========================================================

def get_poi(df, bias):

    poi = None

    for i in range(len(df)-10, len(df)-2):

        # Bearish OB
        if bias == "BEARISH":

            if (
                df["close"].iloc[i] < df["open"].iloc[i]
                and df["high"].iloc[i] > df["high"].iloc[i-1]
            ):

                poi = {
                    "type": "BEARISH OB",
                    "price": df["high"].iloc[i]
                }

        # Bullish OB
        elif bias == "BULLISH":

            if (
                df["close"].iloc[i] > df["open"].iloc[i]
                and df["low"].iloc[i] < df["low"].iloc[i-1]
            ):

                poi = {
                    "type": "BULLISH OB",
                    "price": df["low"].iloc[i]
                }

    return poi

# =========================================================
# POI TAP
# =========================================================

def poi_tap(price, poi, bias):

    if poi is None:
        return False

    if bias == "BEARISH":

        if price >= poi["price"] - 5:
            return True

    elif bias == "BULLISH":

        if price <= poi["price"] + 5:
            return True

    return False

# =========================================================
# LIQUIDITY SWEEP
# =========================================================

def liquidity_sweep(df):

    prev_high = df["high"].iloc[-3]
    prev_low = df["low"].iloc[-3]

    current_high = df["high"].iloc[-1]
    current_low = df["low"].iloc[-1]

    current_close = df["close"].iloc[-1]

    # BUY SIDE SWEEP
    if current_high > prev_high:

        if current_close < prev_high:

            return {
                "valid": True,
                "type": "BUY SIDE SWEEP"
            }

    # SELL SIDE SWEEP
    if current_low < prev_low:

        if current_close > prev_low:

            return {
                "valid": True,
                "type": "SELL SIDE SWEEP"
            }

    return {
        "valid": False
    }

# =========================================================
# MSS
# =========================================================

def detect_mss(df, bias):

    recent_high = df["high"].iloc[-5:].max()
    recent_low = df["low"].iloc[-5:].min()

    current_price = df["close"].iloc[-1]

    # Bullish MSS
    if bias == "BULLISH":

        if current_price > recent_high:

            return {
                "valid": True,
                "type": "BULLISH MSS"
            }

    # Bearish MSS
    elif bias == "BEARISH":

        if current_price < recent_low:

            return {
                "valid": True,
                "type": "BEARISH MSS"
            }

    return {
        "valid": False
    }

# =========================================================
# FVG DETECTION
# =========================================================

def detect_fvg(df, bias):

    for i in range(2, len(df)-1):

        # Bullish FVG
        if bias == "BULLISH":

            if df["high"].iloc[i-2] < df["low"].iloc[i]:

                return "BULLISH FVG"

        # Bearish FVG
        elif bias == "BEARISH":

            if df["low"].iloc[i-2] > df["high"].iloc[i]:

                return "BEARISH FVG"

    return "NO FVG"

# =========================================================
# ENTRY MODEL
# =========================================================

def entry_model(df, bias):

    price = df["close"].iloc[-1]

    # BUY
    if bias == "BULLISH":

        sl = price - (price * 0.003)
        tp = price + (price * 0.009)

        return {
            "side": "BUY",
            "entry": round(price, 2),
            "sl": round(sl, 2),
            "tp": round(tp, 2)
        }

    # SELL
    elif bias == "BEARISH":

        sl = price + (price * 0.003)
        tp = price - (price * 0.009)

        return {
            "side": "SELL",
            "entry": round(price, 2),
            "sl": round(sl, 2),
            "tp": round(tp, 2)
        }

    return None

# =========================================================
# MAIN LOOP
# =========================================================

print("ICT AI BOT STARTED...")

while True:

    try:

        for SYMBOL in SYMBOLS:

            print("\n===================================")
            print("CHECKING:", SYMBOL)
            print("===================================")

            # =========================================
            # FETCH DATA
            # =========================================

            htf_df = get_candles(SYMBOL, "15m")
            ltf_df = get_candles(SYMBOL, "1m")

            if htf_df is None or ltf_df is None:

                print("NO DATA")

                continue

            # =========================================
            # SESSION
            # =========================================

            session = session_filter()

            print("SESSION:", session)

            # =========================================
            # BIAS
            # =========================================

            bias = get_htf_bias(htf_df)

            print("HTF BIAS:", bias)

            # =========================================
            # POI
            # =========================================

            poi = get_poi(htf_df, bias)

            print("HTF POI:", poi)

            # =========================================
            # CURRENT PRICE
            # =========================================

            current_price = ltf_df["close"].iloc[-1]

            print("CURRENT PRICE:", current_price)

            # =========================================
            # POI TAP
            # =========================================

            tapped = poi_tap(current_price, poi, bias)

            print("POI TAPPED:", tapped)

            # =========================================
            # SWEEP
            # =========================================

            sweep = liquidity_sweep(ltf_df)

            print("SWEEP:", sweep)

            # =========================================
            # MSS
            # =========================================

            mss = detect_mss(ltf_df, bias)

            print("MSS:", mss)

            # =========================================
            # FVG
            # =========================================

            fvg = detect_fvg(ltf_df, bias)

            print("FVG:", fvg)

            # =========================================
            # FINAL CONFIRMATION
            # =========================================

            setup_ready = False

            if (
                tapped
                and sweep["valid"]
                and mss["valid"]
                and bias in fvg
            ):

                setup_ready = True

            # =========================================
            # ENTRY
            # =========================================

            if setup_ready:

                entry = entry_model(
                    ltf_df,
                    bias
                )

                msg = f"""
ICT AI BOT ALERT

PAIR: {SYMBOL}

ENTRY: {entry['side']}

ENTRY PRICE: {entry['entry']}

STOP LOSS: {entry['sl']}

TAKE PROFIT: {entry['tp']}

SESSION: {session}

HTF BIAS: {bias}

MSS: {mss['type']}

FVG: {fvg}
"""

                print(msg)

                send_telegram(msg)

            else:

                print("NO VALID ENTRY")

            # =========================================
            # WAIT SYMBOL
            # =========================================

            time.sleep(3)

        # =============================================
        # LOOP WAIT
        # =============================================

        print("\nWAITING NEXT SCAN...\n")

        time.sleep(10)

    except Exception as e:

        print("MAIN LOOP ERROR:", e)

        time.sleep(5)

