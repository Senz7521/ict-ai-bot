import ccxt

exchange = ccxt.bybit({
    "apiKey": "n40XJzeSxB2mttbbBE",
    "secret": "6Qq3AZUYzPRcYuyxmc204TL8inSVcvsiLfPl",
    "enableRateLimit": True,
    "options": {
        "defaultType": "linear"
    }
})

balance = exchange.fetch_balance()

print(balance)