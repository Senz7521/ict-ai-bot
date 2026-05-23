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
    "apiKey": "ys0rRIwJSyDFilMG1GvVzUygnN4rIYhJxwyKSpp57aeLqh7k47O2Y2roCXTf6Xid" 
    "secret": "Y4DlhhLHdS27v6yFkvZruCnKlgkG9gRNkHzPREpB6jXrAOxhn9aYIZp3S6ViMuor",
    "options": {
        "defaultType": "future"
    }
})

balance = exchange.fetch_balance()

print(balance)

balance = exchange.fetch_balance()

print(balance["USDT"])