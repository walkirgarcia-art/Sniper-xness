import os
import time
import threading
import requests
import yfinance as yf
from flask import Flask

TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
CHAT_ID = os.environ['TELEGRAM_CHAT_ID']

PARES = [
    'EURUSD=X', 'GBPUSD=X', 'USDJPY=X', 'XAUUSD=X', 
    'BTC-USD', 'ETH-USD'
]

app = Flask(__name__)

def send_telegram(msg):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    data = {'chat_id': CHAT_ID, 'text': msg, 'parse_mode': 'Markdown', 'disable_web_page_preview': True}
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
        
        buy = anterior['EMA9'] < anterior['EMA21'] and ultima['EMA9'] > ultima['EMA21']
        sell = anterior['EMA9'] > anterior['EMA21'] and ultima['EMA9'] < ultima['EMA21']
        
        precio = round(ultima['Close'], 5)
        nombre = simbolo.replace('=X', '').replace('-USD', '/USD')
        
        # Link genérico Exness WebTerminal
        base_link = 'https://my.exness.com/pa/trading/web'
        links = {
            'EURUSD': f'{base_link}?symbol=EURUSD',
            'GBPUSD': f'{base_link}?symbol=GBPUSD',
            'USDJPY': f'{base_link}?symbol=USDJPY',
            'XAUUSD': f'{base_link}?symbol=XAUUSD',
            'BTC/USD': f'{base_link}?symbol=BTCUSD',
            'ETH/USD': f'{base_link}?symbol=ETHUSD'
        }
        
        link = links.get(nombre, base_link)
        
        if buy:
            return f"🟢 *COMPRA* {nombre}\nPrecio: {precio}\nCruce EMA9 > EMA21 M15\n[Operar ahora]({link})"
        elif sell:
            return f"🔴 *VENTA* {nombre}\nPrecio: {precio}\nCruce EMA21 > EMA9 M15\n[Operar ahora]({link})"
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
            time.sleep(2)
        time.sleep(600)

@app.route('/')
def home():
    return "Sniper Exness Bot Running"

if __name__ == '__main__':
    hilo = threading.Thread(target=sniper_loop)
    hilo.daemon = True
    hilo.start()
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
