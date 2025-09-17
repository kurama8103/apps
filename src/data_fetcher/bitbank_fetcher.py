import requests
import sys
import json

def get_bitbank_orderbook(pair):
    """
    bitbankのパブリックAPIから板情報を取得する。
    """
    endpoint = "https://public.bitbank.cc"
    path = f"/{pair}/depth"

    try:
        response = requests.get(endpoint + path)
        response.raise_for_status()  # HTTPエラーがあれば例外を発生させる
        data = response.json()
        if data.get("success") == 1:
            return data["data"]
        else:
            print(f"API error: {data}", file=sys.stderr)
            return None
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        return None
    except json.JSONDecodeError:
        print("Failed to decode JSON response.", file=sys.stderr)
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python bitbank_fetcher.py <pair>", file=sys.stderr)
        print("Example: python bitbank_fetcher.py btc_jpy", file=sys.stderr)
        sys.exit(1)

    pair = sys.argv[1].lower()
    orderbook = get_bitbank_orderbook(pair)

    if orderbook:
        print(json.dumps(orderbook, indent=2))
