# 設定ファイル

# 取引所の設定
EXCHANGES = {
    "gmo": {
        "api_endpoint": "https://api.coin.z.com/public",
        "fee_rate": 0.0005,  # Taker手数料の例
    },
    "bitbank": {
        "api_endpoint": "https://public.bitbank.cc",
        "fee_rate": 0.0012,  # Taker手数料の例
    }
}

# 監視対象の通貨ペア
# キーは共通のシンボル名、値は各取引所での表現
TARGET_PAIRS = {
    "BTC": {
        "gmo": "BTC",
        "bitbank": "btc_jpy"
    }
    # 今後、他の通貨ペア（例: ETH）を追加可能
    # "ETH": {
    #     "gmo": "ETH",
    #     "bitbank": "eth_jpy"
    # }
}

# その他の設定
LOG_LEVEL = "INFO"
