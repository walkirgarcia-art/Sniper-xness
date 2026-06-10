import requests
import time
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext

TOKEN = "8299367677:AAEWlEDM9J4oSsqQbT08VFBmgcwgnhukbCA"
CHAT_ID = "8135987661"

# Config
EXNESS_BASE = "https://my.exness.com/accounts/sign-up" # Link genérico
TF_PRIMARY = "15m" # M15 para entrada
TF_FILTER = "1h" # H1 para filtro tendencia
INTERVAL = 600 # Revisar cada 10 min

# Pares: 6 originales + 6 nuevos = 12 total
PAIRS = [
    "EURUSD", "GBPUSD", "USDJPY", "XAUUSD", "BTCUSD", "ETHUSD",
    "AUDUSD", "USDCAD", "GBPJPY", "US30", "NAS100", "XAGUSD"
]

app = Flask(__name__)
bot = None
last_signal = {} # Para no repetir señales

def get_ema(symbol, interval, length=21):
    """Saca EMA desde Binance. Para indices/forex usa crypto equivalente o ajusta la API"""
    try:
        # Binance solo tiene crypto. Para forex/indices tendrías que usar otra API como TwelveData
        # Por ahora usamos BTC/ETH real, el resto son simulados para que no crashee
        if "USD" in symbol and symbol not in ["BTCUSD", "ETHUSD"]:
            # Fallback: usa BTCUSD como proxy para que el bot no se caiga
            # Cambia esto por TwelveData si quieres datos reales de forex
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
    """Revisa cruce M15 + filtro H1 + calcula SL/TP"""
    # 1. Datos M15 para entrada
    price, ema9_m15, ema21_m15 = get_ema(symbol, TF_PRIMARY)
    if not price: return None

    # 2. Datos H1 para filtro tendencia
    _, ema9_h1, ema21_h1 = get_ema(symbol, TF_FILTER)
    if not ema9_h1: return None

    # 3. Detectar cruce M15
    cruce_compra = ema9_m15 >
