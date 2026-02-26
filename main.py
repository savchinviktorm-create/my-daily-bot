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

def get_mono_currency():
    try:
        url = "https://api.monobank.ua/bank/currency"
        with urllib.request.urlopen(url, timeout=10) as f:
            data = json.loads(f.read().decode())
            usd = next(item for item in data if item['currencyCodeA'] == 840 and item['currencyCodeB'] == 980)
            eur = next(item for item in data if item['currencyCodeA'] == 978 and item['currencyCodeB'] == 980)
            return f"🔹 <b>Monobank:</b>\n💵 USD: {usd['rateBuy']}/{usd['rateSell']}\n💶 EUR: {eur['rateBuy']}/{eur['rateSell']}"
    except: return "🔹 <b>Monobank:</b> тимчасово недоступний"

def get_privat_currency():
    try:
        # Готівковий курс ПриватБанку
        url = "https://api.privatbank.ua/p24api/pubinfo?exchange&coursid=5"
        with urllib.request.urlopen(url, timeout=10) as f:
            data = json.loads(f.read().decode())
            usd = next(item for item in data if item['ccy'] == 'USD')
            eur = next(item for item in data if item['ccy'] == 'EUR')
            return f"🔸 <b>ПриватБанк:</b>\n💵 USD: {float(usd['buy']):.2f}/{float(usd['sale']):.2f}\n💶 EUR: {float(eur['buy']):.2f}/{float(eur['sale']):.2f}"
    except: return "🔸 <b>ПриватБанк:</b> тимчасово недоступний"

def get_line_by_date(file_name, default_msg):
    """Шукає рядок, що починається з поточної дати (ДД.ММ)."""
    today_prefix = datetime.now().strftime('%d.%m')
    if os.path.exists(file_name):
        with open(file_name, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip().startswith(today_prefix):
                    return line.strip()
    return f"{today_prefix}: {default_msg}"

def get_random_line(file_name, default_text):
    if os.path.exists(file_name):
        with open(file_name, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]
            return random.choice(lines) if lines else default_text
    return default_text

def days_to_new_year():
    now = datetime.now()
    ny_date = datetime(now.year + 1, 1, 1)
    diff = ny_date - now
    return f"🎄 До Нового року залишилося: <b>{diff.days}</b> днів!"

def send_telegram(token, chat_id, text):
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        params = {'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML'}
        data = urllib.parse.urlencode(params).encode()
        urllib.request.urlopen(urllib.request.Request(url, data=data), timeout=15)
        return True
    except Exception as e:
        print(f"Помилка відправки: {e}")
        return False

if __name__ == "__main__":
    TOKEN = os.environ.get("TOKEN", "").strip()
    CHAT_ID = os.environ.get("MY_CHAT_ID", "").strip()
    W_KEY = os.environ.get("WEATHER_API_KEY", "").strip()

    date_full = datetime.now().strftime('%d.%m.%Y')
    
    report = [
        f"📅 <b>ЗВІТ НА {date_full}</b>\n",
        get_weather("Головецько", 49.19, 23.46, W_KEY),
        get_weather("Львів", 49.83, 24.02, W_KEY) + "\n",
        
        "💰 <b>Курс валют для порівняння:</b>",
        get_mono_currency(),
        get_privat_currency() + "\n",
        
        "😇 <b>Іменини сьогодні:</b>",
        get_line_by_date("names.txt", "немає даних про іменини") + "\n",
        
        "📜 <b>Цей день в історії:</b>",
        get_line_by_date("history.txt", "сьогодні спокійний день в історії...") + "\n",
        
        "💡 <b>Цитата дня:</b>",
        f"<i>\"{get_random_line('database.txt', 'Живи сьогодні!')}\"</i>\n",
        
        "😂 <b>Анекдот дня:</b>",
        get_random_line("jokes.txt", "Сьогодні без жартів...") + "\n",
        
        days_to_new_year() + "\n",
        "<i>Бот працює стабільно! ✅</i>"
    ]

    send_telegram(TOKEN, CHAT_ID, "\n".join(report))
