import ccxt

exchange = ccxt.bybit({
    "apiKey": "n40XJzeSxB2mttbbBE",
    "secret": "6Qq3AZUYzPRcYuyxmc204TL8inSVcvsiLfPl",
    "enableRateLimit": True
})

markets = exchange.load_markets()

print("CONNECTED")
print(list(markets.keys())[:10])