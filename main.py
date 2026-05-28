from flask import Flask
import requests
import os
import yfinance as yf
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator, ADXIndicator

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

    data = btc.history(period="2d", interval="5m")

    close_prices = data["Close"]
    high_prices = data["High"]
    low_prices = data["Low"]
    open_prices = data["Open"]

    # RSI
    rsi = RSIIndicator(close_prices, window=14)
    current_rsi = rsi.rsi().iloc[-1]

    # EMA
    ema20 = EMAIndicator(close_prices, window=20)
    ema50 = EMAIndicator(close_prices, window=50)
    ema200 = EMAIndicator(close_prices, window=200)

    current_ema20 = ema20.ema_indicator().iloc[-1]
    current_ema50 = ema50.ema_indicator().iloc[-1]
    current_ema200 = ema200.ema_indicator().iloc[-1]

    # ADX
    adx = ADXIndicator(
        high=high_prices,
        low=low_prices,
        close=close_prices,
        window=14
    )

    current_adx = adx.adx().iloc[-1]

    current_price = close_prices.iloc[-1]

    # Bougie actuelle
    current_open = open_prices.iloc[-1]
    current_close = close_prices.iloc[-1]
    current_high = high_prices.iloc[-1]
    current_low = low_prices.iloc[-1]

    candle_size = abs(current_close - current_open)

    # Moyenne des 5 dernières bougies
    avg_candle_size = (
        abs(close_prices.iloc[-6:-1] - open_prices.iloc[-6:-1])
    ).mean()

    market_behavior = "⚪ NORMAL"

    # Impulsion haussière
    if (
        current_close > current_open
        and candle_size > avg_candle_size * 1.8
    ):

        market_behavior = "🚀 IMPULSION HAUSSIÈRE"

    # Impulsion baissière
    elif (
        current_close < current_open
        and candle_size > avg_candle_size * 1.8
    ):

        market_behavior = "🔥 IMPULSION BAISSIÈRE"

    # Ralentissement / épuisement
    elif candle_size < avg_candle_size * 0.5:

        market_behavior = "🕯️ RALENTISSEMENT / ÉPUISEMENT"

    market_mode = "⚪ NEUTRE"

    # BUY tendance
    if (
        current_ema20 > current_ema50 > current_ema200
        and current_price >= current_ema50 * 0.995
        and 40 < current_rsi < 60
        and current_adx > 25
    ):

        market_mode = "📈 BUY TENDANCE"

    # SELL tendance
    elif (
        current_ema20 < current_ema50 < current_ema200
        and current_price <= current_ema50 * 1.005
        and 40 < current_rsi < 60
        and current_adx > 25
    ):

        market_mode = "📉 SELL TENDANCE"

    # BUY extrême
    elif (
        current_rsi < 25
        and current_adx > 25
    ):

        market_mode = "🔥 BUY EXTRÊME"

    # SELL extrême
    elif (
        current_rsi > 75
        and current_adx > 25
    ):

        market_mode = "🔥 SELL EXTRÊME"

    message = f"""
🚀 SNIPER FOREX AI BOT

📊 BTCUSD Prix :
{current_price:.2f}

📈 RSI :
{current_rsi:.2f}

📉 ADX :
{current_adx:.2f}

📊 EMA20 :
{current_ema20:.2f}

📊 EMA50 :
{current_ema50:.2f}

📊 EMA200 :
{current_ema200:.2f}

🧠 Analyse :
{market_mode}

🔥 Comportement marché :
{market_behavior}
"""

    send_telegram_message(message)

    return "SMART MARKET WORKING"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
