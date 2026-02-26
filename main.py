import os
import json
import random
import urllib.request
import urllib.parse
import re
from datetime import datetime

def get_okko_fuel():
    try:
        # Заходимо на сторінку з цінами
        url = "https://www.okko.ua/fuel"
        headers = {'User-Agent': 'Mozilla/5.0'}
        req = urllib.request.Request(url, headers=headers)
        
        with urllib.request.urlopen(req, timeout=15) as f:
            html = f.read().decode('utf-8')
            
            # Шукаємо ціни за допомогою регулярних виразів
            # Цей метод шукає назву пального та цифри після неї в коді сторінки
            def find_price(type_name):
                match = re.search(fr'{type_name}.*?([\d.,]+)', html, re.DOTALL)
                return match.group(1).replace(',', '.') if match else "—"

            p_95 = find_price("Pulls 95")
            a_95 = find_price("А-95")
            diesel = find_price("Pulls Diesel")
            gas = find_price("ГАЗ")
            
            return (f"⛽ <b>Ціни ОККО:</b>\n"
                    f"🔹 P95: {p_95} грн\n"
                    f"🔹 А95: {a_95} грн\n"
                    f"🔹 ДП Pulls: {diesel} грн\n"
                    f"🔹 ГАЗ: {gas} грн")
    except:
        return "⛽ <b>Ціни ОККО:</b> тимчасово недоступні"

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
            return f"🔹 <b>Mono:</b> USD {usd['rateBuy']}/{usd['rateSell']} | EUR {eur['rateBuy']}/{eur['rateSell']}"
    except: return "🔹 <b>Mono:</b> недоступний"

def get_privat_currency():
    try:
        url = "https://api.privatbank.ua/p24api/pubinfo?exchange&coursid=5"
        with urllib.request.urlopen(url, timeout=10) as f:
            data = json.loads(f.read().decode())
            usd = next(item for item in data if item['ccy'] == 'USD')
            eur = next(item for item in data if item['ccy'] == 'EUR')
            return f"🔸 <b>Приват:</b> USD {float(usd['buy']):.2f}/{float(usd['sale']):.2f} | EUR {float(eur['buy']):.2f}/{float(eur['sale']):.2f}"
    except: return "🔸 <b>Приват:</b> недоступний"

def get_horoscope():
    try:
        signs = {"Овен":"♈","Телець":"♉","Близнюки":"♊","Рак":"♋","Лев":"♌","Діва":"♍","Терези":"♎","Скорпіон":"♏","Стрілець":"♐","Козоріг":"♑","Водолій":"♒","Риби":"♓"}
        advices = ["Вдалий день для справ.", "Будьте обережні з витратами.", "Час для спілкування.", "Краще відпочити.", "Лідерство сьогодні за вами.", "Здоров'я понад усе."]
        text = "<b>✨ Гороскоп:</b>\n"
        for s, e in signs.items(): text += f"{e}{s}: {random.choice(advices)}\n"
        return text
    except: return "✨ Гороскоп недоступний"

def get_line_by_date(file_name, default_msg):
    today = datetime.now().strftime('%d.%m')
    if os.path.exists(file_name):
        with open(file_name, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip().startswith(today): return line.strip()
    return f"{today}: {default_msg}"

def get_random_line(file_name, default_text):
    if os.path.exists(file_name):
        with open(file_name, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]
            return random.choice(lines) if lines else default_text
    return default_text

def send_telegram(token, chat_id, text):
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        params = {'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML'}
        data = urllib.parse.urlencode(params).encode()
        with urllib.request.urlopen(urllib.request.Request(url, data=data), timeout=15) as f: return True
    except: return False

if __name__ == "__main__":
    TOKEN = os.environ.get("TOKEN", "").strip()
    CHAT_ID = os.environ.get("MY_CHAT_ID", "").strip()
    W_KEY = os.environ.get("WEATHER_API_KEY", "").strip()

    now_hour = (datetime.now().hour + 2) % 24
    date_f = datetime.now().strftime('%d.%m.%Y')
    
    weather = [get_weather("Головецько", 49.19, 23.46, W_KEY), get_weather("Львів", 49.83, 24.02, W_KEY)]
    currency = ["💰 <b>Курс валют:</b>", get_mono_currency(), get_privat_currency()]

    if now_hour >= 14:
        # Денний звіт + Пальне
        report = [
            f"🌤 <b>ДЕННИЙ ОГЛЯД ({date_f})</b>\n",
            *weather,
            "\n" + "\n".join(currency),
            "\n" + get_okko_fuel(),
            "\n<i>Гарного дня! ✅</i>"
        ]
    else:
        # Ранковий звіт
        report = [
            f"📅 <b>РАНКОВИЙ ЗВІТ ({date_f})</b>\n",
            *weather, "\n" + "\n".join(currency) + "\n",
            "😇 <b>Іменини:</b> " + get_line_by_date("names.txt", "немає"),
            "📜 <b>Історія:</b> " + get_line_by_date("history.txt", "спокійно") + "\n",
            get_horoscope() + "\n",
            "💡 <b>Цитата:</b> <i>\"" + get_random_line('database.txt', 'Живи!') + "\"</i>",
            "😂 <b>Анекдот:</b> " + get_random_line("jokes.txt", "немає") + "\n",
            "🎄 До НР: <b>" + str((datetime(datetime.now().year+1,1,1)-datetime.now()).days) + "</b> днів",
            "\n<i>Бот працює стабільно! ✅</i>"
        ]

    send_telegram(TOKEN, CHAT_ID, "\n".join(report))
