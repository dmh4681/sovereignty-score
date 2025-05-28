# utils.py
import requests

def get_current_btc_price():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {"ids": "bitcoin", "vs_currencies": "usd"}
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return data["bitcoin"]["usd"]
    except Exception as e:
        print("⚠️ Failed to fetch BTC price:", e)
        return None

def usd_to_sats(usd_amount, btc_price):
    return int((usd_amount / btc_price) * 100_000_000)
