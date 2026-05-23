import ccxt
import pandas as pd
import time

exchange = ccxt.bybit({
    "apiKey": "n40XJzeSxB2mttbbBE",
    "secret": "******",
    "enableRateLimit": True
})

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