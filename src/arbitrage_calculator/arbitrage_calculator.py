import json

def find_arbitrage_opportunity(gmo_orderbook, bitbank_orderbook, gmo_fee_rate=0.0005, bitbank_fee_rate=0.0012):
    """
    GMOコインとbitbankの板情報から裁定取引の機会を見つける。
    手数料を考慮して利益が出るかを判断する。

    :param gmo_orderbook: GMOコインの板情報
    :param bitbank_orderbook: bitbankの板情報
    :param gmo_fee_rate: GMOコインの取引手数料率
    :param bitbank_fee_rate: bitbankの取引手数料率
    :return: 裁定機会に関する情報のリスト
    """
    opportunities = []

    # --- ケース1: GMOで買ってbitbankで売る ---
    if gmo_orderbook.get('asks') and gmo_orderbook['asks'] and bitbank_orderbook.get('bids') and bitbank_orderbook['bids']:
        # GMOの最安売り注文
        gmo_lowest_ask_price = float(gmo_orderbook['asks'][0]['price'])
        gmo_lowest_ask_size = float(gmo_orderbook['asks'][0]['size'])

        # bitbankの最高買い注文
        bitbank_highest_bid_price = float(bitbank_orderbook['bids'][0][0])
        bitbank_highest_bid_size = float(bitbank_orderbook['bids'][0][1])

        # 手数料を考慮した後の価格
        buy_price_with_fee = gmo_lowest_ask_price * (1 + gmo_fee_rate)
        sell_price_with_fee = bitbank_highest_bid_price * (1 - bitbank_fee_rate)

        if sell_price_with_fee > buy_price_with_fee:
            profit_per_unit = sell_price_with_fee - buy_price_with_fee
            tradable_volume = min(gmo_lowest_ask_size, bitbank_highest_bid_size)
            potential_profit = profit_per_unit * tradable_volume

            opportunities.append({
                "type": "Buy GMO, Sell bitbank",
                "buy_exchange": "GMO",
                "sell_exchange": "bitbank",
                "buy_price": gmo_lowest_ask_price,
                "sell_price": bitbank_highest_bid_price,
                "profit_per_unit": profit_per_unit,
                "tradable_volume": tradable_volume,
                "potential_profit": potential_profit,
            })

    # --- ケース2: bitbankで買ってGMOで売る ---
    if bitbank_orderbook.get('asks') and bitbank_orderbook['asks'] and gmo_orderbook.get('bids') and gmo_orderbook['bids']:
        # bitbankの最安売り注文
        bitbank_lowest_ask_price = float(bitbank_orderbook['asks'][0][0])
        bitbank_lowest_ask_size = float(bitbank_orderbook['asks'][0][1])

        # GMOの最高買い注文
        gmo_highest_bid_price = float(gmo_orderbook['bids'][0]['price'])
        gmo_highest_bid_size = float(gmo_orderbook['bids'][0]['size'])

        # 手数料を考慮した後の価格
        buy_price_with_fee = bitbank_lowest_ask_price * (1 + bitbank_fee_rate)
        sell_price_with_fee = gmo_highest_bid_price * (1 - gmo_fee_rate)

        if sell_price_with_fee > buy_price_with_fee:
            profit_per_unit = sell_price_with_fee - buy_price_with_fee
            tradable_volume = min(bitbank_lowest_ask_size, gmo_highest_bid_size)
            potential_profit = profit_per_unit * tradable_volume

            opportunities.append({
                "type": "Buy bitbank, Sell GMO",
                "buy_exchange": "bitbank",
                "sell_exchange": "GMO",
                "buy_price": bitbank_lowest_ask_price,
                "sell_price": gmo_highest_bid_price,
                "profit_per_unit": profit_per_unit,
                "tradable_volume": tradable_volume,
                "potential_profit": potential_profit,
            })

    return opportunities

if __name__ == '__main__':
    # --- Test Case 1: Arbitrage opportunity exists (Buy GMO, Sell bitbank) ---
    print("--- Testing Case 1: Buy GMO (1005000), Sell bitbank (1008000) ---")
    mock_gmo_case1 = {
        "asks": [{"price": "1005000", "size": "0.1"}],
        "bids": [{"price": "1000000", "size": "0.2"}]
    }
    mock_bitbank_case1 = {
        "asks": [["1010000", "0.3"]],
        "bids": [["1008000", "0.4"]]
    }
    opportunities1 = find_arbitrage_opportunity(mock_gmo_case1, mock_bitbank_case1)
    if opportunities1:
        print(json.dumps(opportunities1, indent=2))
    else:
        print("No arbitrage opportunity found.")

    # --- Test Case 2: No arbitrage opportunity ---
    print("\n--- Testing Case 2: No opportunity ---")
    mock_gmo_case2 = {
        "asks": [{"price": "1010000", "size": "0.1"}],
        "bids": [{"price": "1005000", "size": "0.2"}]
    }
    mock_bitbank_case2 = {
        "asks": [["1012000", "0.3"]],
        "bids": [["1008000", "0.4"]]
    }
    opportunities2 = find_arbitrage_opportunity(mock_gmo_case2, mock_bitbank_case2)
    if opportunities2:
        print(json.dumps(opportunities2, indent=2))
    else:
        print("No arbitrage opportunity found.")

    # --- Test Case 3: Arbitrage opportunity exists (Buy bitbank, Sell GMO) ---
    print("\n--- Testing Case 3: Buy bitbank (1010000), Sell GMO (1012000) ---")
    mock_gmo_case3 = {
        "asks": [{"price": "1015000", "size": "0.1"}],
        "bids": [{"price": "1012000", "size": "0.2"}]
    }
    mock_bitbank_case3 = {
        "asks": [["1010000", "0.3"]],
        "bids": [["1008000", "0.4"]]
    }
    opportunities3 = find_arbitrage_opportunity(mock_gmo_case3, mock_bitbank_case3)
    if opportunities3:
        print(json.dumps(opportunities3, indent=2))
    else:
        print("No arbitrage opportunity found.")
