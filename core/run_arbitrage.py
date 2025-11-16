import sys
import json
from .src.config import config
from .src.data_fetcher.gmo_fetcher import get_gmo_orderbook
from .src.data_fetcher.bitbank_fetcher import get_bitbank_orderbook
from .src.arbitrage_calculator.arbitrage_calculator import find_arbitrage_opportunity

def main():
    """
    メイン処理。データ取得から裁定計算までを実行する。
    """
    # 設定ファイルから最初のターゲットペアを取得
    if not config.TARGET_PAIRS:
        print("設定ファイルにターゲットペアが定義されていません。", file=sys.stderr)
        sys.exit(1)

    target_symbol = list(config.TARGET_PAIRS.keys())[0]
    pair_details = config.TARGET_PAIRS[target_symbol]

    print(f"--- {target_symbol}の価格情報を取得しています... ---")

    # GMOコインから板情報を取得
    gmo_symbol = pair_details.get("gmo")
    if not gmo_symbol:
        print(f"GMOコインの{target_symbol}シンボルが設定されていません。", file=sys.stderr)
        return

    print("GMOコインから取得中...")
    gmo_data = get_gmo_orderbook(gmo_symbol)
    if not gmo_data or gmo_data.get("status") != 0:
        print("GMOコインからのデータ取得に失敗しました。", file=sys.stderr)
        if gmo_data:
            print(f"エラー詳細: {gmo_data}", file=sys.stderr)
        return
    gmo_orderbook = gmo_data['data']
    print("GMOコインから取得完了。")


    # bitbankから板情報を取得
    bitbank_pair = pair_details.get("bitbank")
    if not bitbank_pair:
        print(f"bitbankの{target_symbol}ペアが設定されていません。", file=sys.stderr)
        return

    print("bitbankから取得中...")
    bitbank_orderbook = get_bitbank_orderbook(bitbank_pair)
    if not bitbank_orderbook:
        print("bitbankからのデータ取得に失敗しました。", file=sys.stderr)
        return
    print("bitbankから取得完了。")

    print("\n--- 裁定機会を計算しています... ---")

    # 手数料率を設定から取得
    gmo_fee = config.EXCHANGES.get("gmo", {}).get("fee_rate", 0)
    bitbank_fee = config.EXCHANGES.get("bitbank", {}).get("fee_rate", 0)

    # 裁定機会を計算
    opportunities = find_arbitrage_opportunity(gmo_orderbook, bitbank_orderbook, gmo_fee, bitbank_fee)

    if opportunities:
        print("裁定取引の機会が見つかりました！")
        print(json.dumps(opportunities, indent=2, ensure_ascii=False))
    else:
        print("裁定取引の機会は見つかりませんでした。")
        # 参考までに現在の最良気配値を表示
        gmo_ask = gmo_orderbook.get('asks')[0]['price'] if gmo_orderbook.get('asks') else 'N/A'
        gmo_bid = gmo_orderbook.get('bids')[0]['price'] if gmo_orderbook.get('bids') else 'N/A'
        bb_ask = bitbank_orderbook.get('asks')[0][0] if bitbank_orderbook.get('asks') else 'N/A'
        bb_bid = bitbank_orderbook.get('bids')[0][0] if bitbank_orderbook.get('bids') else 'N/A'
        print("\n参考価格:")
        print(f"  GMO Best Ask: {gmo_ask}, Best Bid: {gmo_bid}")
        print(f"  bitbank Best Ask: {bb_ask}, Best Bid: {bb_bid}")


if __name__ == "__main__":
    main()
