# =========================================================
# ICT AI BOT + DELTA EXCHANGE + TELEGRAM
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

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": msg
    }

    requests.post(url, data=data)

# =========================================================
# DELTA EXCHANGE
# =========================================================

exchange = ccxt.bybit({
    "options": {
        "defaultType": "future"
    },
    "enableRateLimit": True
})
# =========================================================
# SYMBOL
# =========================================================

SYMBOLS = [
    "BTC/USDT",
    "ETH/USDT",
    "XAU/USD"
]

# =========================================================
# FETCH CANDLES
# =========================================================

def get_candles(symbol, timeframe, limit=100):

    try:

        ohlcv = exchange.fetch_ohlcv(
            symbol,
            timeframe=timeframe,
            limit=limit
        )

        if not ohlcv:
            return None

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

    except Exception as e:

        print("CANDLE ERROR:", e)

        return None

# =========================================================
# SESSION FILTER
# =========================================================

def session_filter():

    utc_hour = datetime.utcnow().hour

    if 7 <= utc_hour <= 11:
        return "LONDON"

    elif 12 <= utc_hour <= 16:
        return "NEW_YORK"

    else:
        return "DEAD_SESSION"

# =========================================================
# HTF BIAS
# =========================================================

def get_htf_bias(df):

    if len(df) < 20:

        return {
            "bias": "NEUTRAL"
        }

    last_high = df["high"].iloc[-2]
    old_high = df["high"].iloc[-10]

    last_low = df["low"].iloc[-2]
    old_low = df["low"].iloc[-10]

    # =====================================================
    # BULLISH
    # =====================================================

    if last_high > old_high:

        return {
            "bias": "BULLISH"
        }

    # =====================================================
    # BEARISH
    # =====================================================

    elif last_low < old_low:

        return {
            "bias": "BEARISH"
        }

    return {
        "bias": "NEUTRAL"
    }

# =========================================================
# HTF POI
# =========================================================

def get_htf_poi(df, bias):

    if len(df) < 5:
        return None

    candle_high = df["high"].iloc[-3]
    candle_low = df["low"].iloc[-3]

    if bias == "BULLISH":

        return {
            "type": "BULLISH_OB",
            "high": candle_high,
            "low": candle_low
        }

    elif bias == "BEARISH":

        return {
            "type": "BEARISH_OB",
            "high": candle_high,
            "low": candle_low
        }

    return None

# =========================================================
# INSIDE POI
# =========================================================

def inside_poi(price, poi):

    if poi is None:
        return False

    if poi["low"] <= price <= poi["high"]:
        return True

    return False

# =========================================================
# LIQUIDITY SWEEP
# =========================================================

def liquidity_sweep(df):

    if len(df) < 5:

        return {
            "valid": False
        }

    prev_high = df["high"].iloc[-3]
    prev_low = df["low"].iloc[-3]

    current_high = df["high"].iloc[-1]
    current_low = df["low"].iloc[-1]

    current_close = df["close"].iloc[-1]

    # =====================================================
    # BUY SIDE SWEEP
    # =====================================================

    if current_high > prev_high:

        if current_close < prev_high:

            return {
                "type": "BUY_SIDE_SWEEP",
                "valid": True
            }

    # =====================================================
    # SELL SIDE SWEEP
    # =====================================================

    if current_low < prev_low:

        if current_close > prev_low:

            return {
                "type": "SELL_SIDE_SWEEP",
                "valid": True
            }

    return {
        "valid": False
    }

# =========================================================
# MSS DETECTION
# =========================================================

def detect_mss(df, bias):

    if len(df) < 10:

        return {
            "valid": False
        }

    current_close = df["close"].iloc[-1]

    swing_high = df["high"].iloc[-4]
    swing_low = df["low"].iloc[-4]

    # =====================================================
    # BULLISH MSS
    # =====================================================

    if bias == "BULLISH":

        if current_close > swing_high:

            return {
                "type": "BULLISH_MSS",
                "valid": True
            }

    # =====================================================
    # BEARISH MSS
    # =====================================================

    if bias == "BEARISH":

        if current_close < swing_low:

            return {
                "type": "BEARISH_MSS",
                "valid": True
            }

    return {
        "valid": False
    }

# =========================================================
# ENTRY MODEL
# =========================================================

def entry_model(df, bias):

    current_price = df["close"].iloc[-1]

    # =====================================================
    # BUY
    # =====================================================

    if bias == "BULLISH":

        return {
            "entry": "BUY",
            "price": current_price,
            "sl": current_price - 100,
            "tp": current_price + 300
        }

    # =====================================================
    # SELL
    # =====================================================

    if bias == "BEARISH":

        return {
            "entry": "SELL",
            "price": current_price,
            "sl": current_price + 100,
            "tp": current_price - 300
        }

    return None

# =========================================================
# MAIN LOOP
# =========================================================
while True:

    try:

        # =================================================
        # GET DATA
        # =================================================

        for SYMBOL in SYMBOLS:
            htf_df = get_candles(SYMBOL, "15m")
            ltf_df = get_candles(SYMBOL, "1m")

        # =================================================
        # DATA CHECK
        # =================================================

        if htf_df is None or ltf_df is None:

            print("\nNO DATA RECEIVED")

            time.sleep(5)

            continue

        # =================================================
        # SESSION
        # =================================================

        session = session_filter()

        print("\n==============================")
        print("SESSION BOX")
        print("==============================")
        print(session)

        # =================================================
        # HTF BIAS
        # =================================================

        bias_data = get_htf_bias(htf_df)

        bias = bias_data["bias"]

        print("\n==============================")
        print("HTF BIAS BOX")
        print("==============================")
        print(bias)

        # =================================================
        # HTF POI
        # =================================================

        htf_poi = get_htf_poi(htf_df, bias)

        print("\n==============================")
        print("HTF POI BOX")
        print("==============================")
        print(htf_poi)

        # =================================================
        # CURRENT PRICE
        # =================================================

        current_price = ltf_df["close"].iloc[-1]

        # =================================================
        # POI CHECK
        # =================================================

        poi_valid = inside_poi(
            current_price,
            htf_poi
        )

        print("\n==============================")
        print("POI CHECK")
        print("==============================")
        print(poi_valid)

        # =================================================
        # LIQUIDITY SWEEP
        # =================================================

        sweep = liquidity_sweep(ltf_df)

        print("\n==============================")
        print("LIQUIDITY SWEEP BOX")
        print("==============================")
        print(sweep)

        # =================================================
        # MSS
        # =================================================

        mss = detect_mss(ltf_df, bias)

        print("\n==============================")
        print("MSS BOX")
        print("==============================")
        print(mss)

        # =================================================
        # FINAL ENTRY
        # =================================================

        if (
            poi_valid
            and sweep["valid"]
            and mss["valid"]
        ):

            entry = entry_model(
                ltf_df,
                bias
            )

            print("\n==============================")
            print("FINAL ENTRY BOX")
            print("==============================")
            print(entry)

            # =============================================
            # TELEGRAM ALERT
            # =============================================

            send_telegram(str(entry))

        else:

            print("\nNO VALID ENTRY")

        # =================================================
        # WAIT
        # =================================================

        time.sleep(10)

    except Exception as e:

        print("\nERROR:", e)

        time.sleep(5)