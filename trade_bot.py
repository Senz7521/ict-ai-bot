import ccxt

exchange = ccxt.binance({
    "apiKey": "px2SKqNJnFWlSBvNoosgA8WebKNzbc9B9TjyKx5ql1D5aXjaC6Z4rAyCnFMRCrw6",
    "secret": "D2tLp6uMQwFgmTv4mg4XB63prwNt3DoHb4JnzlgLDujMMPFtUNIcFNiObhQRLbkr",
    "options": {
        "defaultType": "future"
    }
})
import ccxt

exchange = ccxt.binance({
    "apiKey": "023984",
    "secret": "HdA8qVvrQPTT1ZN3RwmKlzHRyXJ0m4H38JghC0HU8Q6U49jOe4ZOKNJpcgaOaiBr",
    "options": {
        "defaultType": "future"
    }
})

balance = exchange.fetch_balance()

print(balance)

balance = exchange.fetch_balance()

print(balance["USDT"])