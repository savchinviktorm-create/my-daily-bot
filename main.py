import os
import json
import random
import urllib.request
import urllib.parse
import re
from datetime import datetime

def get_fuel_prices():
    """Спрощений парсинг з резервними даними"""
    try:
        url = "https://vseazs.com/ua/oil/prices/1"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as f:
            html = f.read().decode('utf-8')
            res = re.findall(r'([\d,.]+)', html)
            # Беремо реальні цифри, якщо вони схожі на ціни пального (40-70 грн)
            prices = [p.replace(',', '.') for p in res if 20 < float(p.replace(',', '.')) < 80]
            if len(prices) >= 3:
                return f"⛽ <b>Ціни на пальне:</b>\n🔹 А-95: {prices[0]} грн\n🔹 ДП: {prices[1]} грн\n🔹 ГАЗ: {prices[2]} грн"
    except: pass
    return "⛽ <b>Пальне:</b> орієнтовно А95 ~55.50, ДП ~52.10, ГАЗ ~28.50"

def get_weather(city, lat, lon, key):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={key}&units=metric&lang=uk"
        with urllib.request.urlopen(url, timeout=10) as f:
            data = json.loads(f.read().decode())
            temp = round(data['main']['temp'])
            return f"📍 {city}: {'+' if temp > 0 else ''}{temp}°C, {data['weather'][0]['description'].capitalize()}"
    except: return f"📍 {city}: дані недоступні"

def get_mono_currency():
    try:
        url = "https://api.monobank.ua/bank/currency"
        with urllib.request.urlopen(url, timeout=10) as f:
            data = json.loads(f.read().decode())
            usd = next(item for item in data if item['currencyCodeA'] == 840 and item['currencyCodeB'] == 980)
            return f"💵 USD: {usd['rateBuy']}/{usd['rateSell']}"
    except: return "💵 USD: недоступно"

def send_telegram(token, chat_id, text):
    """Функція з виводом помилок у консоль GitHub"""
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        params = {'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML'}
        data = urllib.parse.urlencode(params).encode()
        req = urllib.request.Request(url, data=data)
        with urllib.request.urlopen(req, timeout=15) as f:
            print("Telegram response OK")
            return True
    except Exception as e:
        print(f"TELEGRAM ERROR: {e}") # Це ми побачимо в логах GitHub
        return False

if __name__ == "__main__":
    TOKEN = os.environ.get("TOKEN", "").strip()
    CHAT_ID = os.environ.get("MY_CHAT_ID", "").strip()
    W_KEY = os.environ.get("WEATHER_API_KEY", "").strip()

    # Перевірка наявності ключів
    if not TOKEN or not CHAT_ID:
        print("CRITICAL ERROR: TOKEN or CHAT_ID is missing in Secrets!")
    
    date_str = datetime.now().strftime('%d.%m.%Y')
    
    report = [
        f"📊 <b>ЗВІТ НА {date_str}</b>\n",
        get_weather("Головецько", 49.19, 23.46, W_KEY),
        get_weather("Львів", 49.83, 24.02, W_KEY),
        "\n💰 <b>Курс валют:</b>",
        get_mono_currency(),
        "\n" + get_fuel_prices(),
        "\nБот працює стабільно! ✅"
    ]

    success = send_telegram(TOKEN, CHAT_ID, "\n".join(report))
    if not success:
        # Спроба відправити коротке повідомлення без HTML, якщо велике не пройшло
        send_telegram(TOKEN, CHAT_ID, "Помилка форматування HTML, але бот живий!")
