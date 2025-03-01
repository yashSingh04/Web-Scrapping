import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# ✅ FastAPI Backend URL
BACKEND_URL = "http://127.0.0.1:8000"

st.title("🪙 Indian Crypto Market (CoinDCX)")

crypto_symbol = st.text_input("Enter Crypto Symbol (e.g., BTC, ETH, DOGE)", "BTC").upper()

def fetch_live_crypto(symbol):
    try:
        url = f"https://api.coindcx.com/exchange/ticker"
        response = requests.get(url)
        data = response.json()
        market_data = next((item for item in data if item["market"] == f"{symbol}USDT"), None)
        if market_data:
            return {"price": float(market_data["last_price"]), "volume": float(market_data["volume"])}
        return None
    except:
        return None

def fetch_crypto_history(symbol):
    try:
        url = f"{BACKEND_URL}/crypto/history/{symbol}"
        response = requests.get(url)
        data = response.json()
        if "error" in data:
            return None
        return pd.DataFrame(data)
    except:
        return None

live_data = fetch_live_crypto(crypto_symbol)
if live_data:
    st.subheader(f"💰 {crypto_symbol} Price in USDT: ${live_data['price']:,.2f}")
    st.subheader(f"📊 24h Volume: {live_data['volume']:,.2f}")
else:
    st.warning("Live data not available!")

st.subheader(f"📈 {crypto_symbol} Price & Volume History (30m Interval, Last 1 Month)")
history_data = fetch_crypto_history(crypto_symbol)

if history_data is not None and not history_data.empty:
    fig_price = px.line(history_data, x="date", y="close", title=f"{crypto_symbol} Price (USDT)", labels={"date": "Date", "close": "Price (USDT)"})
    st.plotly_chart(fig_price)

    fig_volume = px.bar(history_data, x="date", y="volume", title=f"{crypto_symbol} Trading Volume", labels={"date": "Date", "volume": "Volume"})
    st.plotly_chart(fig_volume)

    # ✅ Download Excel Button
    excel_url = f"{BACKEND_URL}/crypto/history/excel/{crypto_symbol}"
    st.markdown(f"[📥 Download Excel Data]( {excel_url} )", unsafe_allow_html=True)
else:
    st.warning("No historical data available!")
