import ccxt

exchange = ccxt.bybit({
    "apiKey": "YOUR_API_KEY",
    "secret": "YOUR_SECRET_KEY",
    "enableRateLimit": True
})

markets = exchange.load_markets()

print("CONNECTED")
print(list(markets.keys())[:10])