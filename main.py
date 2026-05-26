from flask import Flask
import requests
import os

app = Flask(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = "TON_CHAT_ID"

message = "🚀 SNIPER FOREX AI BOT CONNECTED"

url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

data = {
    "chat_id": CHAT_ID,
    "text": message
}

try:
    requests.post(url, data=data)
except:
    print("Erreur Telegram")

@app.route('/')
def home():
    return "BOT IS RUNNING"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
