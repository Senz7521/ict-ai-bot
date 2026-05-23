 import ccxt
import pandas as pd
import time

def new_func():
    exchange = ccxt.bybit({
    "apiKey": "MJFbQ47VjMvvApEBG0",
    "secret": "KWqVRuKV4p1BLFYA21EVhEjCVkmu33ht6N28",
    "enableRateLimit": True,
})
    
    return exchange

exchange = new_func()

# DEMO MODE
exchange.set_sandbox_mode(True)

ticker = exchange.fetch_ticker("BTC/USDT")

print(ticker)

SYMBOL = "BTC/USDT"
TIMEFRAME = "1m"

while True:

    ohlcv = exchange.fetch_ohlcv(SYMBOL, TIMEFRAME, limit=100)

    df = pd.DataFrame(
        ohlcv,
        columns=["time","open","high","low","close","volume"]
    )

    print(df.tail())

    time.sleep(10)