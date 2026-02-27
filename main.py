import os
import urllib.request
import json
import csv
import io
import re
from datetime import datetime

# Пряме посилання на твій CSV
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSExxHF9GN-lpJF9I3L9kLzFoH9lo4_emwtiEoHpiezlf3ESOw6dxGrjmQwk1wuFC6mV6035wu6-l4M/pub?gid=2060076239&single=true&output=csv"

def get_data(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.read().decode('utf-8')
    except: return None

def parse_currency():
    raw = get_data(URL_CSV)
    if not raw: return "❌ Таблиця недоступна"
    
    # Перетворюємо CSV на один плоский список усіх значень
    f = io.StringIO(raw)
    reader = csv.reader(f)
    flat_list = []
    for row in reader:
        flat_list.extend([cell.strip() for cell in row if cell.strip()])

    usd_b, eur_b = 0.0, 0.0
    res = {"USD": "н/д", "EUR": "н/д"}

    for i, word in enumerate(flat_list):
        # Шукаємо USD/EUR і беремо цифри, що йдуть ПІСЛЯ них
        if word.upper() in ["USD", "EUR"]:
            try:
                # Склеюємо цілу частину і копійки (напр. 43 і 0500)
                buy = f"{flat_list[i+1]}.{flat_list[i+2][:2]}"
                sale = f"{flat_list[i+3]}.{flat_list[i+4][:2]}"
                res[word.upper()] = f"{buy} / {sale}"
                if word.upper() == "USD": usd_b = float(buy)
                if word.upper() == "EUR": eur_b = float(buy)
            except: continue

    cross = round(eur_b / usd_b, 3) if usd_b > 0 else "н/д"
    return f"🇺🇸 **USD:** {res['USD']}\n🇪🇺 **EUR:** {res['EUR']}\n💱 **Крос-курс:** {cross}"

def get_weather():
    key = os.getenv('WEATHER_API_KEY')
    locs = [("Головецько", "lat=49.20&lon=23.45"), ("Львів", "q=Lviv")]
    out = []
    for name, p in locs:
        d = get_data(f"http://api.openweathermap.org/data/2.5/weather?{p}&appid={key}&units=metric&lang=uk")
        if d:
            js = json.loads(d)
            out.append(f"📍 {name}: {round(js['main']['temp'])}°C, {js['weather'][0]['description'].capitalize()}")
    return "\n".join(out)

def get_git_info(file_name, key):
    d = get_data(f"https://raw.githubusercontent.com/savchinviktorm-create/my-daily-bot/main/{file_name}")
    if d:
        for line in d.splitlines():
            if key.lower() in line.lower():
                return line.split('—', 1)[-1].strip() if '—' in line else line.strip()
    return "немає даних"

def send():
    now = datetime.now()
    months = ["січня", "лютого", "березня", "квітня", "травня", "червня", "липня", "серпня", "вересня", "жовтня", "листопада", "грудня"]
    day_month = f"{now.day} {months[now.month-1]}" # "27 лютого"

    msg = (
        f"📅 **ЗВІТ НА {now.strftime('%d.%m.%Y')}**\n\n"
        f"🌡 **Погода:**\n{get_weather()}\n\n"
        f"💰 **Курс (Мінфін):**\n{parse_currency()}\n\n"
        f"😇 **Іменини:**\n{day_month}: {get_git_info('names.txt', day_month)}\n\n"
        f"📜 **Історія:**\n{get_git_info('history.txt', now.strftime('%m-%d'))}\n\n"
        f"🎄 До Нового року: {(datetime(now.year + 1, 1, 1) - now).days} днів!\n\n"
        f"⛽ **Пальне:** А-95: 56.15 | ДП: 52.30 | Газ: 27.85"
    )

    url = f"https://api.telegram.org/bot{os.getenv('TOKEN')}/sendMessage"
    req = urllib.request.Request(url, data=json.dumps({"chat_id": os.getenv('MY_CHAT_ID'), "text": msg, "parse_mode": "Markdown"}).encode('utf-8'),
                                 headers={'Content-Type': 'application/json'})
    urllib.request.urlopen(req)

if __name__ == "__main__":
    send()
