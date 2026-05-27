from flask import Flask
import requests
import os
import yfinance as yf
import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator
import schedule
import time
import threading

app = Flask(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = "7507876088"

pairs = {
    "EURUSD": "EURUSD=X",
    "GBPUSD": "GBPUSD=X",
    "USDJPY": "JPY=X",
    "USDCAD": "CAD=X",
    "AUDUSD": "AUDUSD=X",
    "EURJPY": "EURJPY=X",
    "GBPJPY": "GBPJPY=X",
    "EURGBP": "EURGBP=X",
    "XAUUSD": "GC=F",
    "BTCUSD": "BTC-USD",
    "USTEC": "^NDX",
    "USOIL": "CL=F"
}

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message
    }
    requests.post(url, data=data)

def analyze_market():
    for pair_name, symbol in pairs.items():
        try:
            df = yf.download(symbol, period="1d", interval="5m")

            if len(df) < 50:
                continue

            close = df['Close']

            rsi = RSIIndicator(close, window=14).rsi()
            ema50 = EMAIndicator(close, window=50).ema_indicator()

            current_price = close.iloc[-1]
            current_rsi = rsi.iloc[-1]
            current_ema50 = ema50.iloc[-1]

            buy_signal = current_price > current_ema50 and current_rsi < 30
            sell_signal = current_price < current_ema50 and current_rsi > 70

            if buy_signal:
                send_telegram(
                    f"📈 BUY SIGNAL\n\nPair: {pair_name}\nRSI: {current_rsi:.2f}"
                )

            if sell_signal:
                send_telegram(
                    f"📉 SELL SIGNAL\n\nPair: {pair_name}\nRSI: {current_rsi:.2f}"
                )

        except Exception as e:
            print(f"Erreur sur {pair_name}: {e}")

schedule.every(5).minutes.do(analyze_market)

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

threading.Thread(target=run_scheduler).start()

@app.route('/')
def home():
    return "SNIPER FOREX AI BOT RUNNING"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
