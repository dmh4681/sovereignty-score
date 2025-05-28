import streamlit as st
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
        st.error("⚠️ Failed to fetch Bitcoin price.")
        st.exception(e)
        return None
