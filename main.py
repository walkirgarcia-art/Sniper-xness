import os
import time
import threading
import requests
import yfinance as yf
from flask import Flask

# Variables desde Render
TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
CHAT_ID = os.environ['TELEGRAM_CHAT_ID']

# Pares a monitorear - Exness
PARES = [
    'EURUSD=X', 'GBPUSD=X', 'USDJPY=X', 'XAUUSD=X', 
    'BTC-USD', 'ETH-USD'
]

app = Flask(__name__)

def send_telegram(msg):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    data = {'chat_id': CHAT_ID, 'text': msg, 'parse_mode': 'Markdown'}
    try:
        requests.post(url, data=data, timeout=10)
    except Exception as e:
        print(f"Error Telegram: {e}")

def analizar_par(simbolo):
    try:
        df = yf.download(tickers=simbolo, period='1d', interval='15m', progress=False)
        if len(df) < 20:
            return None
            
        df['EMA9'] = df['Close'].ewm(span=9).mean()
        df['EMA21'] = df['Close'].ewm(span=21).mean()
        
        ultima = df.iloc[-1]
        anterior = df.iloc[-2]
        
        # Cruce alcista
        buy = anterior['EMA9'] < anterior['EMA21'] and ultima['EMA9'] > ultima['EMA21']
        # Cruce bajista  
        sell = anterior['EMA9'] > anterior['EMA21'] and ultima['EMA9'] < ultima['EMA21']
        
        precio = round(ultima['Close'], 5)
        nombre = simbolo.replace('=X', '').replace('-USD', '/USD')
        
        if buy:
            return f"🟢 *COMPRA* {nombre}\nPrecio: {precio}\nCruce EMA9 > EMA21 M15"
        elif sell:
            return f"🔴 *VENTA* {nombre}\nPrecio: {precio}\nCruce EMA21 > EMA9 M15"
        else:
            return None
            
    except Exception as e:
        print(f"Error analizando {simbolo}: {e}")
        return None

def sniper_loop():
    send_telegram("✅ *Sniper Exness activado*\nM15 | Forex + Crypto + Oro\nRevisando cada 10 min")
    while True:
        for par in PARES:
            senal = analizar_par(par)
            if senal:
                send_telegram(senal)
            time.sleep(2)  # No saturar yfinance
        time.sleep(600)  # 10 minutos

@app.route('/')
def home():
    return "Sniper Exness Bot Running"

if __name__ == '__main__':
    # Arranca el sniper en segundo plano
    hilo = threading.Thread(target=sniper_loop)
    hilo.daemon = True
    hilo.start()
    # Arranca Flask para que Render no apague el servicio
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
