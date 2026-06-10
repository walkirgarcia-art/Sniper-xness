import requests
import time
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext

TOKEN = "8299367677:AAEWlEDM9J4oSsqQbT08VFBmgcwgnhukbCA"
CHAT_ID = "8135987661"

EXNESS_BASE = "https://my.exness.com/accounts/sign-up"
TF_PRIMARY = "15m"
TF_FILTER = "1h"
INTERVAL = 600

PAIRS = [
    "EURUSD", "GBPUSD", "USDJPY", "XAUUSD", "BTCUSD", "ETHUSD",
    "AUDUSD", "USDCAD", "GBPJPY", "US30", "NAS100", "XAGUSD"
]

app = Flask(__name__)
bot = None
last_signal = {}

def get_ema(symbol, interval):
    try:
        if "USD" in symbol and symbol not in ["BTCUSD", "ETHUSD"]:
            symbol = "BTCUSD"

        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit=50"
        data = requests.get(url, timeout=10).json()
        closes = [float(c[4]) for c in data]

        ema9 = sum(closes[-9:]) / 9
        ema21 = sum(closes[-21:]) / 21
        price = closes[-1]
        return price, ema9, ema21
    except:
        return None, None, None

def check_signal(symbol):
    price, ema9_m15, ema21_m15 = get_ema(symbol, TF_PRIMARY)
    if not price:
        return None

    _, ema9_h1, ema21_h1 = get_ema(symbol, TF_FILTER)
    if not ema9_h1:
        return None

    cruce_compra = ema9_m15 > ema21_m15 and last_signal.get(symbol)!= "COMPRA"
    cruce_venta = ema9_m15 < ema21_m15 and last_signal.get(symbol)!= "VENTA"

    if cruce_compra and ema9_h1 > ema21_h1:
        tipo = "COMPRA"
        sl = round(ema21_m15, 5)
        tp = round(price + (price - sl) * 2, 5)
        emoji = "🟢"
    elif cruce_venta and ema9_h1 < ema21_h1:
        tipo = "VENTA"
        sl = round(ema21_m15, 5)
        tp = round(price - (sl - price) * 2, 5)
        emoji = "🔴"
    else:
        return None

    last_signal[symbol] = tipo

    msg = f"{emoji} {tipo} {symbol}\n"
    msg += f"Precio: {price}\n"
    msg += f"SL: {sl} | TP: {tp}\n"
    msg += f"Riesgo 1:2 | M15 + Filtro H1"

    keyboard = [[InlineKeyboardButton("Operar ahora", url=EXNESS_BASE)]]
    return msg, InlineKeyboardMarkup(keyboard)

def sniper_loop():
    global bot
    time.sleep(5)
    while True:
        for pair in PAIRS:
            try:
                result = check_signal(pair)
                if result:
                    msg, markup = result
                    bot.send_message(chat_id=CHAT_ID, text=msg, reply_markup=markup)
                    time.sleep(2)
            except Exception as e:
                print(f"Error en {pair}: {e}")
        time.sleep(INTERVAL)

@app.route('/')
def home():
    return "Sniper Exness v2 Activo"

def start_bot():
    global bot
    updater = Updater(TOKEN, use_context=True)
    bot = updater.bot

    bot.send_message(
        chat_id=CHAT_ID,
        text="✅ Sniper Exness v2 activado\nM15 + Filtro H1 | 12 Pares | SL/TP 1:2\nRevisando cada 10 min"
    )

    threading.Thread(target=sniper_loop, daemon=True).start()
    updater.start_polling()

if __name__ == '__main__':
    threading.Thread(target=start_bot, daemon=True).start()
    app.run(host='0.0.0.0', port=10000)
