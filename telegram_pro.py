# =========================================================
# TELEGRAM PRO ENGINE
# FILE NAME : telegram_pro.py
# =========================================================

import requests
from datetime import datetime

# =========================================================
# TELEGRAM CONFIG
# =========================================================

TOKEN = "8854671551:AAGOwQ3waewFoQzadtwuJRBAVJNEOPKUkx0"
CHAT_ID = "5240659041"

# =========================================================
# SEND TELEGRAM
# =========================================================

def send_telegram(message):

    try:

        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

        data = {

            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "HTML"

        }

        requests.post(url, data=data)

    except:

        pass

# =========================================================
# PRO SIGNAL ALERT
# =========================================================

def send_entry_alert(

    pair,
    bias,
    entry_model,
    session,
    entry,
    sl,
    tp1,
    score,
    htf_poi,
    ltf_mss,
    micro_poi

):

    message = f"""

🚨 <b>ICT AI BOT PRO ALERT</b>

━━━━━━━━━━━━━━━

💱 PAIR : <b>{pair}</b>

📊 HTF BIAS : <b>{bias}</b>

🧠 ENTRY MODEL : <b>{entry_model}</b>

🌍 SESSION : <b>{session}</b>

━━━━━━━━━━━━━━━

🎯 ENTRY : <b>{entry}</b>

🛑 SL : <b>{sl}</b>

✅ TP1 : <b>{tp1}</b>

━━━━━━━━━━━━━━━

📦 HTF POI : <b>{htf_poi}</b>

⚡ LTF MSS : <b>{ltf_mss}</b>

🎯 MICRO POI : <b>{micro_poi}</b>

━━━━━━━━━━━━━━━

🔥 AI CONFIDENCE : <b>{score}%</b>

📅 DATE : {datetime.now().strftime("%d-%m-%Y")}

⏰ TIME : {datetime.now().strftime("%H:%M:%S")}

━━━━━━━━━━━━━━━

⚠️ STRICT SMART MONEY MODEL
⚠️ TRADE WITH RISK MANAGEMENT

"""

    send_telegram(message)

# =========================================================
# TP HIT ALERT
# =========================================================

def send_tp_hit(pair,tp):

    message = f"""

🏆 TP HIT

💱 PAIR : {pair}

🎯 TARGET HIT : {tp}

🔥 ICT AI BOT

"""

    send_telegram(message)

# =========================================================
# SL HIT ALERT
# =========================================================

def send_sl_hit(pair,sl):

    message = f"""

❌ STOP LOSS HIT

💱 PAIR : {pair}

🛑 SL : {sl}

⚠️ NEXT SETUP LOADING...

"""

    send_telegram(message)

# =========================================================
# DAILY BIAS POST
# =========================================================

def send_daily_bias(

    btc_bias,
    eth_bias,
    gold_bias

):

    message = f"""

🌎 DAILY ICT MARKET BIAS

━━━━━━━━━━━━━━━

🟢 BTC : {btc_bias}

🟣 ETH : {eth_bias}

🟡 GOLD : {gold_bias}

━━━━━━━━━━━━━━━

⚡ POWERED BY ICT AI BOT

"""

    send_telegram(message)

# =========================================================
# WEEKLY RESULT POST
# =========================================================

def send_weekly_results(

    wins,
    losses,
    rr,
    pnl

):

    message = f"""

📈 WEEKLY RESULTS

━━━━━━━━━━━━━━━

✅ WINS : {wins}

❌ LOSSES : {losses}

⚖️ RR : {rr}

💰 PNL : {pnl}

━━━━━━━━━━━━━━━

🔥 STRICT ICT EXECUTION

"""

    send_telegram(message)