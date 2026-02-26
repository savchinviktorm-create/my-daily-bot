import os
import json
import random
import urllib.request
import urllib.parse
from datetime import datetime

def get_weather(city, lat, lon, key):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={key}&units=metric&lang=uk"
        with urllib.request.urlopen(url, timeout=10) as f:
            data = json.loads(f.read().decode())
            temp = round(data['main']['temp'])
            desc = data['weather'][0]['description'].capitalize()
            return f"📍 {city}: {'+' if temp > 0 else ''}{temp}°C, {desc}"
    except: return f"📍 {city}: дані недоступні"

def get_currency():
    try:
        url = "https://api.monobank.ua/bank/currency"
        with urllib.request.urlopen(url, timeout=10) as f:
            data = json.loads(f.read().decode())
            # Коди валют: 840 - USD, 978 - EUR, 980 - UAH
            usd = next(item for item in data if item['currencyCodeA'] == 840 and item['currencyCodeB'] == 980)
            eur = next(item for item in data if item['currencyCodeA'] == 978 and item['currencyCodeB'] == 980)
            return f"💵 USD: {usd['rateBuy']}/{usd['rateSell']}\n💶 EUR: {eur['rateBuy']}/{eur['rateSell']}"
    except: return "📈 Курс валют: тимчасово недоступний"

def get_random_line(file_name, default_text):
    if os.path.exists(file_name):
        with open(file_name, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]
            return random.choice(lines) if lines else default_text
    return default_text

def send_telegram(token, chat_id, text):
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = urllib.parse.urlencode({'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML'}).encode()
        urllib.request.urlopen(urllib.request.Request(url, data=data), timeout=10)
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    TOKEN = os.environ.get("TOKEN", "").strip()
    CHAT_ID = os.environ.get("MY_CHAT_ID", "").strip()
    W_KEY = os.environ.get("WEATHER_API_KEY", "").strip()

    date_str = datetime.now().strftime('%d.%m.%Y')
    
    # Збираємо звіт
    report = [
        f"<b>ЗВІТ НА {date_str}</b>\n",
        get_weather("Головецько", 49.19, 23.46, W_KEY),
        get_weather("Львів", 49.83, 24.02, W_KEY) + "\n",
        "<b>Курс валют (Mono):</b>",
        get_currency() + "\n",
        "<b>😇 Іменини сьогодні:</b>",
        get_random_line("names.txt", "Інформація про іменини відсутня") + "\n",
        "<b>😂 Анекдот дня:</b>",
        get_random_line("jokes.txt", "Сьогодні без жартів...") + "\n",
        "<i>Бот працює стабільно! ✅</i>"
    ]

    full_text = "\n".join(report)
    
    if send_telegram(TOKEN, CHAT_ID, full_text):
        print("Done!")
    else:
        exit(1)
