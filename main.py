from flask import Flask
import requests
import os
import yfinance as yf

app = Flask(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = "7507876088"

def send_telegram_message(message):

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": message
    }

    requests.post(url, data=data)

@app.route("/")
def home():

    btc = yf.Ticker("BTC-USD")

    data = btc.history(period="1d")

    last_price = data["Close"].iloc[-1]

    message = f"""
🚀 SNIPER FOREX AI BOT

✅ Connexion marché réussie

📊 BTCUSD Prix actuel :
{last_price:.2f}
"""

    send_telegram_message(message)

    return "MARKET DATA WORKING"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
