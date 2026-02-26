import os
import json
import random
import urllib.request
import urllib.parse
from datetime import datetime, timedelta

# Твоє перевірене посилання на Google Таблицю
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSExxHF9GN-lpJF9I3L9kLzFoH9lo4_emwtiEoHpiezlf3ESOw6dxGrjmQwk1wuFC6mV6035wu6-l4M/pub?gid=0&single=true&output=csv"

def get_fuel_from_sheets():
    try:
        req = urllib.request.Request(SHEET_CSV_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as f:
            content = f.read().decode('utf-8').splitlines()
            def extract(line_idx):
                row = content[line_idx].split(',')
                return row[2].replace('"', '').strip()
            # Рядки в CSV: 1(95+), 2(95), 4(ДП), 5(Газ)
            return (f"⛽ <b>Ціни на пальне:</b>\n"
                    f"🔹 А-95+: {extract(1)} грн\n"
                    f"🔹 А-95: {extract(2)} грн\n"
                    f"🔹 ДП: {extract(4)} грн\n"
                    f"🔹 ГАЗ: {extract(5)} грн")
    except:
        return "⛽ <b>Пальне:</b> дані оновлюються..."

def get_weather(city, lat, lon, key):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={key}&units=metric&lang=uk"
        with urllib.request.urlopen(url, timeout=10) as f:
            data = json.loads(f.read().decode())
            t = round(data['main']['temp'])
            return f"📍 {city}: {'+' if t > 0 else ''}{t}°C, {data['weather'][0]['description'].capitalize()}"
    except: return f"📍 {city}: недоступна"

def get_mono():
    try:
        url = "https://api.monobank.ua/bank/currency"
        with urllib.request.urlopen(url, timeout=10) as f:
            data = json.loads(f.read().decode())
            usd = next(item for item in data if item['currencyCodeA'] == 840 and item['currencyCodeB'] == 980)
            return f"💵 USD: {usd['rateBuy']}/{usd['rateSell']}"
    except: return "💵 USD: недоступно"

def get_line_by_date(file_name, default_msg):
    try:
        today = datetime.now().strftime('%d.%m')
        if os.path.exists(file_name):
            with open(file_name, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip().startswith(today):
                        return line.strip()
        return f"{today}: {default_msg}"
    except: return default_msg

def get_random_line(file_name, default_text):
    try:
        if os.path.exists(file_name):
            with open(file_name, 'r', encoding='utf-8') as f:
                lines = [l.strip() for l in f if l.strip()]
                if lines: return random.choice(lines)
        return default_text
    except: return default_text

def get_horoscope():
    advices = ["Вдалий день для починань.", "Будьте обережні з фінансами.", "Час для відпочинку.", "Можливі приємні сюрпризи.", "Зосередьтесь на головному."]
    signs = {"Овен":"♈","Телець":"♉","Близнюки":"♊","Рак":"♋","Лев":"♌","Діва":"♍","Терези":"♎","Скорпіон":"♏","Стрілець":"♐","Козоріг":"♑","Водолій":"♒","Риби":"♓"}
    res = "<b>✨ Гороскоп:</b>\n"
    for s, e in signs.items():
        res += f"{e} {s}: {random.choice(advices)}\n"
    return res

if __name__ == "__main__":
    TOKEN = os.
