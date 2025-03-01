from fastapi import FastAPI
import requests
import pandas as pd
import time
from datetime import datetime, timedelta
from fastapi.responses import FileResponse

app = FastAPI()

# ✅ CoinDCX API URL
COINDCX_CANDLE_API = "https://public.coindcx.com/market_data/candles"

@app.get("/crypto/history/{symbol}")
def get_crypto_history(symbol: str):
    try:
        coindcx_symbol = f"B-{symbol.upper()}_USDT"

        end_time = int(time.time() * 1000)  # Current timestamp in ms
        start_time = int((datetime.now() - timedelta(days=30)).timestamp() * 1000)  # 30 days ago in ms

        params = {
            "pair": coindcx_symbol,
            "interval": "30m",
            "startTime": start_time,
            "endTime": end_time,
            "limit": 1000,
        }

        response = requests.get(COINDCX_CANDLE_API, params=params)
        data = response.json()

        if not data:
            return {"error": "No historical data available"}

        history_data = [
            {
                "date": pd.to_datetime(entry["time"], unit="ms"),
                "open": entry["open"],
                "high": entry["high"],
                "low": entry["low"],
                "close": entry["close"],
                "volume": entry["volume"],
            }
            for entry in data
        ]

        return history_data

    except Exception as e:
        return {"error": str(e)}

# ✅ Generate & Download Excel File
@app.get("/crypto/history/excel/{symbol}")
def download_crypto_excel(symbol: str):
    try:
        history_data = get_crypto_history(symbol)

        if "error" in history_data:
            return {"error": "No data available for export"}

        df = pd.DataFrame(history_data)
        filename = f"{symbol.upper()}_history.xlsx"
        file_path = f"./{filename}"

        df.to_excel(file_path, index=False)

        return FileResponse(file_path, filename=filename, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    except Exception as e:
        return {"error": str(e)}
