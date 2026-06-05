from flask import Flask
import requests
import os
import yfinance as yf
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator, ADXIndicator
from ta.volatility import AverageTrueRange
import threading
import time
app = Flask(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = "7507876088"

# Mémoire anti-spam
last_signals = {}
last_heartbeat = 0
def send_telegram_message(message):

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": message
    }

    requests.post(url, data=data)

# Liste actifs
assets = {
    "BTCUSD": "BTC-USD",
    "ETHUSD": "ETH-USD",
    "XAUUSD": "GC=F",
    "EURUSD": "EURUSD=X",
    "GBPUSD": "GBPUSD=X",
    "USDJPY": "JPY=X",
    "AUDUSD": "AUDUSD=X",
    "USDCAD": "CAD=X",
    "EURJPY": "EURJPY=X",
    "GBPJPY": "GBPJPY=X",
    "EURGBP": "EURGBP=X",
    "AUDJPY": "AUDJPY=X",
    "CADJPY": "CADJPY=X",
    "USTEC": "^NDX",
    "USOIL": "CL=F"
}

@app.route("/")
def home():

    final_message = ""

    for asset_name, symbol in assets.items():
        print("SCAN:", asset_name)

        try:

            market = yf.Ticker(symbol)

            data = market.history(period="2d", interval="5m")

            if data.empty:
                continue

            close_prices = data["Close"]
            high_prices = data["High"]
            low_prices = data["Low"]
            open_prices = data["Open"]

            current_price = close_prices.iloc[-1]

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

# ATR
            atr = AverageTrueRange(
                high=high_prices,
                low=low_prices,
                close=close_prices,
                window=14
            )

            current_atr = atr.average_true_range().iloc[-1]
# SL Technique
            buy_sl = support - (current_atr * 0.5)
            sell_sl = resistance + (current_atr * 0.5)
            # Bougie actuelle
            current_open = open_prices.iloc[-1]
            current_close = close_prices.iloc[-1]
            current_high = high_prices.iloc[-1]
            current_low = low_prices.iloc[-1]
            previous_open = open_prices.iloc[-2]
            previous_close = close_prices.iloc[-2]
            previous_high = high_prices.iloc[-2]
            previous_low = low_prices.iloc[-2]
            previous_body = abs(previous_close - previous_open)
            previous_range = previous_high - previous_low
            is_doji = (
                previous_body < previous_range * 0.1
            )

            is_exhaustion = (
                previous_body < avg_candle_size * 0.5
            )
            lower_wick = min(previous_open, previous_close) - previous_low
            upper_wick = previous_high - max(previous_open, previous_close)

            long_lower_wick = (
                lower_wick > previous_body * 2
            )

            long_upper_wick = (
                upper_wick > previous_body * 2
            )
            bullish_rejection = (
                long_lower_wick
                or is_doji
                or is_exhaustion
            )

            bearish_rejection = (
                long_upper_wick
                or is_doji
                or is_exhaustion
            )
            near_ema50 = (
                abs(current_price - current_ema50)
                <= current_atr
            )

            near_ema200 = (
                abs(current_price - current_ema200)
                <= current_atr
            )

            near_support = (
                abs(current_price - support)
                <= current_atr
            )

            near_resistance = (
                abs(current_price - resistance)
                <= current_atr
            )
            valid_bullish_rejection = (
                bullish_rejection
                and (
                    near_support
                    or near_ema50
                    or near_ema200
                )
            )

            valid_bearish_rejection = (
                bearish_rejection
                and (
                    near_resistance
                    or near_ema50
                    or near_ema200
                )
            )
            confirmed_buy_setup = (
                valid_bullish_rejection
                and market_behavior == "🚀 IMPULSION HAUSSIÈRE"
            )

            confirmed_sell_setup = (
                valid_bearish_rejection
                and market_behavior == "🔥 IMPULSION BAISSIÈRE"
            )
# TP Zone Clé
            buy_tp = resistance
            sell_tp = support
            candle_size = abs(current_close - current_open)

            avg_candle_size = (
                abs(close_prices.iloc[-6:-1] - open_prices.iloc[-6:-1])
            ).mean()

            market_behavior = "⚪ NORMAL"

            if (
                current_close > current_open
                and candle_size > avg_candle_size * 1.8
            ):

                market_behavior = "🚀 IMPULSION HAUSSIÈRE"

            elif (
                current_close < current_open
                and candle_size > avg_candle_size * 1.8
            ):

                market_behavior = "🔥 IMPULSION BAISSIÈRE"

            elif candle_size < avg_candle_size * 0.5:

                market_behavior = "🕯️ RALENTISSEMENT"

            # Zones
            resistance = high_prices.iloc[-20:].max()
            support = low_prices.iloc[-20:].min()

            zone_analysis = "⚪"

            if current_price >= resistance * 0.998:

                zone_analysis = "📉 RÉSISTANCE"

            elif current_price <= support * 1.002:

                zone_analysis = "📈 SUPPORT"

            # Cassures
            bullish_breakout = (
                current_price > resistance
                and "HAUSSIÈRE" in market_behavior
            )

            bearish_breakout = (
                current_price < support
                and "BAISSIÈRE" in market_behavior
            )

            # SCORE
            confidence = 0

            if (
                current_rsi < 25
                or current_rsi > 75
                or 40 < current_rsi < 60
            ):

                confidence += 20

            if current_adx > 25:

                confidence += 20

            if (
                "SUPPORT" in zone_analysis
                or "RÉSISTANCE" in zone_analysis
            ):

                confidence += 20

            if (
                current_ema20 > current_ema50
                or current_ema20 < current_ema50
            ):

                confidence += 20

            if (
                "IMPULSION" in market_behavior
                or bullish_breakout
                or bearish_breakout
            ):

                confidence += 20

            # Signal
            signal = "⚪ NEUTRE"
            print(asset_name, signal)
            # BUY tendance
            if (
                current_ema20 > current_ema50 > current_ema200
                and current_price >= current_ema50 * 0.995
                and 40 < current_rsi < 60
                and current_adx > 25
                and (
    bullish_breakout
    or confirmed_buy_setup
)
            ):

                signal = "🚀 BUY TENDANCE"

            # SELL tendance
            elif (
                current_ema20 < current_ema50 < current_ema200
                and current_price <= current_ema50 * 1.005
                and 40 < current_rsi < 60
                and current_adx > 25
                and (
    bearish_breakout
    or confirmed_sell_setup
                )
            ):

                signal = "🔥 SELL TENDANCE"

            # BUY extrême
            elif (
                current_rsi < 25
                and current_adx > 25
                and "SUPPORT" in zone_analysis
            ):

                signal = "🔥 BUY EXTRÊME"

            # SELL extrême
            elif (
                current_rsi > 75
                and current_adx > 25
                and "RÉSISTANCE" in zone_analysis
            ):

                signal = "🔥 SELL EXTRÊME"

            # Anti-spam
            previous_signal = last_signals.get(asset_name)

            if (
                signal != "⚪ NEUTRE"
                and signal != previous_signal
            ):

                last_signals[asset_name] = signal

                final_message += f"""
📊 {asset_name}

💰 Prix : {current_price:.2f}

📈 RSI : {current_rsi:.2f}
📉 ADX : {current_adx:.2f}
📊 ATR : {current_atr:.2f}

🧠 Signal :
{signal}
📊 ATR : {current_atr:.2f}
🎯 SL BUY : {buy_sl:.2f}
🎯 SL SELL : {sell_sl:.2f}
🎯 TP BUY : {buy_tp:.2f}
🎯 TP SELL : {sell_tp:.2f}
🎯 Confiance :
{confidence}%

🔥 Comportement :
{market_behavior}

📍 Zone :
{zone_analysis}

------------------------
"""
                
except Exception as e:

    print("ERREUR", asset_name, e)

    continue


    if final_message != "":

        send_telegram_message(
            "🚀 SNIPER FOREX AI BOT\n\n" + final_message
        )

    return "ANTI SPAM ACTIVE"
def auto_scan():

    global last_heartbeat

    while True:

        try:

            home()

            if time.time() - last_heartbeat >= 21600:

                send_telegram_message(
                    "🤖 SNIPER FOREX AI BOT\n\n✅ Scanner actif\n✅ Render actif\n⏰ Heartbeat 6h"
                )

                last_heartbeat = time.time()

        except Exception as e:

            print(e)

        time.sleep(300)

threading.Thread(target=auto_scan).start()
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
