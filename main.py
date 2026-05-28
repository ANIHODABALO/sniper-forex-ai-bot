    from flask import Flask
import requests
import os
import yfinance as yf
import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend port EMAIndicator, ADXIndicator
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

            df = yf.download(symbol, period="2d", interval="5m")

            if len(df) < 200:
                continue

            close = df['Close']
            high = df['High']
            low = df['Low']

            ema20 = EMAIndicator(close, window=20).ema_indicator()
            ema50 = EMAIndicator(close, window=50).ema_indicator()
            ema200 = EMAIndicator(close, window=200).ema_indicator()

            rsi = RSIIndicator(close, window=14).rsi()
port         adx = ADXIndicator(
                high=high,
                low=low,
                close=close,
                window=14
            ).adx()

            current_price = close.iloc[-1]

            current_ema20 = ema20.iloc[-1]
            current_ema50 = ema50.iloc[-1]
            current_ema200 = ema200.iloc[-1]

            current_rsi = rsi.iloc[-1]
            current_adx = adx.iloc[-1]

            bullish_trend = (
                current_ema20 > current_ema50 > current_ema200
            )

            bearish_trend = (
                current_ema20 < current_ema50 < current_ema200
            )

            strong_trend = current_adx > 25

            buy_trend_signal = (
                bullish_trend
                and current_price > current_ema50
                and 40 < current_rsi < 60
                and strong_trend
            )

            sell_trend_signal = (
                bearish_trend
                and current_price < current_ema50
                and 40 < current_rsi < 60
                and strong_trend
            )

            if buy_trend_signal:

                message = f"""
📈 SIGNAL ACHAT — {pair_name}

Type : Pullback Tendance

RSI : {current_rsi:.2f}
ADX : {current_adx:.2f}

✅ Tendance haussière confirmée
✅ EMA20 > EMA50 > EMA200
✅ Prix au-dessus EMA50
✅ Force tendance confirmée

🎯 Opportunité BUY détectée
"""

                send_telegram(message)

            if sell_trend_signal:

                message = f"""
📉 SIGNAL VENTE — {pair_name}

Type : Pullback Tendance

RSI : {current_rsi:.2f}
ADX : {current_adx:.2f}

✅ Tendance baissière confirmée
✅ EMA20 < EMA50 < EMA200
✅ Prix en-dessous EMA50
✅ Force tendance confirmée

🎯 Opportunité SELL détectée
"""

                send_telegram(message)

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
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
