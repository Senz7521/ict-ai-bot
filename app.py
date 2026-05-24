# =========================================================
# TELEGRAM ALERT
# =========================================================

if entry == "BUY" or entry == "SELL":

    entry_price = round(last_close, 2)

    # BUY SETUP
    if entry == "BUY":

        tp1 = round(entry_price + 10, 2)
        tp2 = round(entry_price + 20, 2)
        tp3 = round(entry_price + 35, 2)

        sl = round(entry_price - 10, 2)

        poi_type = "Bullish Order Block"
        entry_model = "Micro Bullish FVG"

    # SELL SETUP
    else:

        tp1 = round(entry_price - 10, 2)
        tp2 = round(entry_price - 20, 2)
        tp3 = round(entry_price - 35, 2)

        sl = round(entry_price + 10, 2)

        poi_type = "Bearish Order Block"
        entry_model = "Micro Bearish FVG"

    # TELEGRAM MESSAGE
   msg = f"""
ICT AI BOT ALERT

PAIR: {selected_pair}

ENTRY: {entry}

ENTRY PRICE: {entry_price}

SL: {sl}

TP: {tp}

CONFIDENCE: {confidence}%

SESSION: {session}

HTF BIAS: {htf_bias}

LTF MSS: {ltf_mss}

POI TYPE: {poi_type}

ENTRY MODEL: {entry_model}

CONFIRMED:
✓ HTF BIAS
✓ POI
✓ LTF POI TAP
✓ LTF MSS
✓ MICRO FVG / OB ENTRY

STATUS: READY FOR ENTRY
"""