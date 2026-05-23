# =========================================================
# ADVANCED ICT AI MODEL
# HTF → HTF POI → LTF SWEEP → MSS → ENTRY
# =========================================================

# =========================================================
# IMPORTS
# =========================================================

import ccxt
import pandas as pd
import numpy as np
import time
from datetime import datetime

# =========================================================
# DELTA EXCHANGE SETUP
# =========================================================

exchange = ccxt.delta({
    "apiKey": "3TrP8raAhYPCi0U4lujmypLONY55Q9",
    "secret": "KyvsnJxeiUtiE0wFPUGTLEg59Z2M91e2QKxSEIpM7chqjFPG5GHW6b7xdwlb",
    "enableRateLimit": True
})

SYMBOL = "BTC/USDT"


# =========================================================
# FETCH CANDLES
# =========================================================

def get_candles(symbol, timeframe, limit=300):

    ohlcv = exchange.fetch_ohlcv(
        symbol,
        timeframe,
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

    return df

# =========================================================
# SESSION FILTER
# LONDON + NEW YORK
# =========================================================

def session_filter():

    utc_hour = datetime.utcnow().hour

    london = 7 <= utc_hour <= 11
    new_york = 12 <= utc_hour <= 16

    if london:
        return "LONDON"

    if new_york:
        return "NEW_YORK"

    return "DEAD_SESSION"

# =========================================================
# DISPLACEMENT DETECTION
# =========================================================

def displacement_filter(df):

    candle_range = (
        df["high"].iloc[-1] -
        df["low"].iloc[-1]
    )

    body = abs(
        df["close"].iloc[-1] -
        df["open"].iloc[-1]
    )

    body_ratio = body / candle_range

    if body_ratio > 0.7:
        return True

    return False

# =========================================================
# EXTERNAL LIQUIDITY
# =========================================================

def external_liquidity(df):

    swing_high = df["high"].rolling(5).max().iloc[-5]
    swing_low = df["low"].rolling(5).min().iloc[-5]

    return {
        "buy_side": swing_high,
        "sell_side": swing_low
    }

# =========================================================
# LIQUIDITY SWEEP DETECTION
# =========================================================

def liquidity_sweep(df):

    previous_high = df["high"].iloc[-3]
    previous_low = df["low"].iloc[-3]

    current_high = df["high"].iloc[-1]
    current_low = df["low"].iloc[-1]

    current_close = df["close"].iloc[-1]

    # =========================================
    # BUY SIDE SWEEP
    # =========================================

    if current_high > previous_high:

        if current_close < previous_high:

            return {
                "sweep": "BUY_SIDE_LIQUIDITY",
                "valid": True
            }

    # =========================================
    # SELL SIDE SWEEP
    # =========================================

    if current_low < previous_low:

        if current_close > previous_low:

            return {
                "sweep": "SELL_SIDE_LIQUIDITY",
                "valid": True
            }

    return {
        "sweep": "NO_SWEEP",
        "valid": False
    }

# =========================================================
# HTF BIAS
# =========================================================

def get_htf_bias(df):

    last_high = df["high"].iloc[-2]
    prev_high = df["high"].iloc[-10]

    last_low = df["low"].iloc[-2]
    prev_low = df["low"].iloc[-10]

    displacement = displacement_filter(df)

    # =========================================
    # BULLISH
    # =========================================

    if last_high > prev_high and displacement:

        return {
            "bias": "BULLISH",
            "structure": "BOS_UP"
        }

    # =========================================
    # BEARISH
    # =========================================

    if last_low < prev_low and displacement:

        return {
            "bias": "BEARISH",
            "structure": "BOS_DOWN"
        }

    return {
        "bias": "NEUTRAL",
        "structure": "RANGE"
    }

# =========================================================
# PREMIUM / DISCOUNT ARRAY
# =========================================================

def pd_array(df):

    dealing_high = df["high"].max()
    dealing_low = df["low"].min()

    equilibrium = (
        dealing_high +
        dealing_low
    ) / 2

    current_price = df["close"].iloc[-1]

    if current_price > equilibrium:
        return "PREMIUM"

    return "DISCOUNT"

# =========================================================
# REAL FVG DETECTION
# =========================================================

def detect_fvg(df, bias):

    candle1_high = df["high"].iloc[-3]
    candle1_low = df["low"].iloc[-3]

    candle3_high = df["high"].iloc[-1]
    candle3_low = df["low"].iloc[-1]

    # =========================================
    # BULLISH FVG
    # =========================================

    if bias == "BULLISH":

        if candle3_low > candle1_high:

            return {
                "type": "BULLISH_FVG",
                "high": candle3_low,
                "low": candle1_high,
                "valid": True
            }

    # =========================================
    # BEARISH FVG
    # =========================================

    if bias == "BEARISH":

        if candle3_high < candle1_low:

            return {
                "type": "BEARISH_FVG",
                "high": candle1_low,
                "low": candle3_high,
                "valid": True
            }

    return {
        "type": "NO_FVG",
        "valid": False
    }

# =========================================================
# MSS DETECTION
# =========================================================

def detect_mss(df, bias):

    current_close = df["close"].iloc[-1]

    swing_high = df["high"].iloc[-4]
    swing_low = df["low"].iloc[-4]

    displacement = displacement_filter(df)

    # =========================================
    # BULLISH MSS
    # =========================================

    if bias == "BULLISH":

        if current_close > swing_high and displacement:

            return {
                "mss": "BULLISH_MSS",
                "valid": True
            }

    # =========================================
    # BEARISH MSS
    # =========================================

    if bias == "BEARISH":

        if current_close < swing_low and displacement:

            return {
                "mss": "BEARISH_MSS",
                "valid": True
            }

    return {
        "mss": "NO_MSS",
        "valid": False
    }

# =========================================================
# HTF POI
# =========================================================

def get_htf_bias(df):

    if len(df) < 20:

        return {
            "bias": "NEUTRAL",
            "structure": "NO_DATA"
        }

    if bias == "BULLISH":

        return {
            "type": "BULLISH_OB",
            "high": df["high"].iloc[-3],
            "low": df["low"].iloc[-3]
        }

    if bias == "BEARISH":

        return {
            "type": "BEARISH_OB",
            "high": df["high"].iloc[-3],
            "low": df["low"].iloc[-3]
        }

# =========================================================
# PRICE INSIDE HTF POI
# =========================================================

def inside_htf_poi(price, poi):

    if poi["low"] <= price <= poi["high"]:
        return True

    return False

# =========================================================
# ENTRY MODEL
# =========================================================

def entry_model(df, bias):

    current_price = df["close"].iloc[-1]

    # =========================================
    # BUY
    # =========================================

    if bias == "BULLISH":

        return {
            "type": "BUY",
            "entry": current_price,
            "sl": current_price - 150,
            "tp1": current_price + 300,
            "tp2": current_price + 600
        }

    # =========================================
    # SELL
    # =========================================

    if bias == "BEARISH":

        return {
            "type": "SELL",
            "entry": current_price,
            "sl": current_price + 150,
            "tp1": current_price - 300,
            "tp2": current_price - 600
        }

# =========================================================
# MAIN LOOP
# =========================================================

while True:

    try:

        # =====================================
        # DATA
        # =====================================

        htf_df = get_candles(SYMBOL, "15m")
        ltf_df = get_candles(SYMBOL, "1m")

        # =====================================
        # SESSION
        # =====================================

        session = session_filter()

        print("\n==============================")
        print("SESSION BOX")
        print("==============================")
        print(session)

        # =====================================
        # HTF BIAS
        # =====================================

        bias_data = get_htf_bias(htf_df)

        print("\n==============================")
        print("HTF BIAS BOX")
        print("==============================")
        print(bias_data)

        bias = bias_data["bias"]

        # =====================================
        # PD ARRAY
        # =====================================

        pd_zone = pd_array(htf_df)

        print("\n==============================")
        print("PREMIUM / DISCOUNT BOX")
        print("==============================")
        print(pd_zone)

        # =====================================
        # HTF POI
        # =====================================

        htf_poi = get_htf_poi(htf_df, bias)

        print("\n==============================")
        print("HTF POI BOX")
        print("==============================")
        print(htf_poi)

        # =====================================
        # LIQUIDITY SWEEP
        # =====================================

        sweep = liquidity_sweep(ltf_df)

        print("\n==============================")
        print("LIQUIDITY SWEEP BOX")
        print("==============================")
        print(sweep)

        # =====================================
        # FVG
        # =====================================

        fvg = detect_fvg(ltf_df, bias)

        print("\n==============================")
        print("FVG BOX")
        print("==============================")
        print(fvg)

        # =====================================
        # MSS
        # =====================================

        mss = detect_mss(ltf_df, bias)

        print("\n==============================")
        print("MSS BOX")
        print("==============================")
        print(mss)

        # =====================================
        # CURRENT PRICE
        # =====================================

        current_price = ltf_df["close"].iloc[-1]

        # =====================================
        # HTF POI CHECK
        # =====================================

        poi_check = inside_htf_poi(
            current_price,
            htf_poi
        )

        # =====================================
        # FINAL ENTRY
        # =====================================

        if (
            session != "DEAD_SESSION"
            and sweep["valid"]
            and fvg["valid"]
            and mss["valid"]
            and poi_check
        ):

            entry = entry_model(
                ltf_df,
                bias
            )

            print("\n==============================")
            print("FINAL ENTRY BOX")
            print("==============================")
            print(entry)

        else:

            print("\nNO VALID ENTRY")

        time.sleep(10)

    except Exception as e:

        print("\nERROR:", e)

        time.sleep(5)