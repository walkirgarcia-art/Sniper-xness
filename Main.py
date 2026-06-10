import os
import requests
import time
import yfinance as yf
import pandas as pd
from flask import Flask
from threading import Thread
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator, ADXIndicator

TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
CHAT_ID = os.environ['TELEGRAM_CHAT_ID']
LINK_BROKER = "https://my.exness.com/webterminal"

PARES = [
    # FOREX
    "EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X", "USDCAD=X", "USDCHF=X", "NZDUSD=X",
    "EURJPY=X", "GBPJPY=X", "EURGBP=X",
    # ORO
    "XAUUSD=X",
    # CRYPTO
    "BTC-USD", "ETH-USD", "SOL-USD", "XRP-USD", "BNB-USD"
]

TEMPORALIDAD = "15m"
ULTIMA_SEÑAL = {}
app = Flask(__name__)

def enviar_telegram(mensaje):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": mensaje, "parse_mode": "HTML", "disable_web_page_preview": True}
    try:
        requests.post(url, data=data, timeout=10)
    except Exception as e:
        print(f"Error Telegram: {e}")

def analizar_par(simbolo):
    try:
        df = yf.download(tickers=simbolo, period="5d", interval=TEMPORALIDAD, progress=False)
        if len(df) < 100: 
            return
            
        df['ema50'] = EMAIndicator(df['Close'], 50).ema_indicator()
        df['ema200'] = EMAIndicator(df['Close'], 200).ema_indicator()
        df['rsi'] = RSIIndicator(df['Close'], 14).rsi()
        df['adx'] = ADXIndicator(df['High'], df['Low'], df['Close'], 14).adx()
        df['atr'] = (df['High'] - df['Low']).rolling(14).mean()
        
        ult = df.iloc[-1]
        ant = df.iloc[-2]
        
        hay_tendencia = ult['adx'] > 25
        tendencia_alcista = ult['Close'] > ult['ema200']
        tendencia_bajista = ult['Close'] < ult['ema200']
        
        buy =
