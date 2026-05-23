import ccxt
import pandas as pd
import time

exchange = ccxt.bybit()

SYMBOL = "BTC/USDT"
TIMEFRAME = "1m"

while True:

    ohlcv = exchange.fetch_ohlcv(SYMBOL, TIMEFRAME, limit=100)

    df = pd.DataFrame(
        ohlcv,
        columns=["time","open","high","low","close","volume"]
    )

    last_close = df["close"].iloc[-1]
    prev_close = df["close"].iloc[-2]

    print("PRICE:", last_close)

    if last_close > prev_close:
        print("BIAS = BULLISH")
    else:
        print("BIAS = BEARISH")

    print("-------------")

    time.sleep(10)