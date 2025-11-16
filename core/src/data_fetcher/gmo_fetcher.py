import requests
import sys
import json

def get_gmo_orderbook(symbol):
    """
    GMOコインのパブリックAPIから板情報を取得する。
    """
    endpoint = "https://api.coin.z.com/public"
    path = f"/v1/orderbooks?symbol={symbol}"

    try:
        response = requests.get(endpoint + path)
        response.raise_for_status()  # HTTPエラーがあれば例外を発生させる
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python gmo_fetcher.py <symbol>", file=sys.stderr)
        print("Example: python gmo_fetcher.py BTC", file=sys.stderr)
        sys.exit(1)

    symbol = sys.argv[1].upper()
    orderbook = get_gmo_orderbook(symbol)

    if orderbook:
        print(json.dumps(orderbook, indent=2))
