import os
import urllib.request
import json
import csv
import io
import re
from datetime import datetime

# Пряме посилання на твій CSV
URL_CURRENCY_TABLE = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSExxHF9GN-lpJF9I3L9kLzFoH9lo4_emwtiEoHpiezlf3ESOw6dxGrjmQwk1wuFC6mV6035wu6-l4M/pub?gid=2060076239&single=true&output=csv"

def get_raw_data(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as response:
            return response.read().decode('utf-8')
    except: return None

def extract_nums(row_list):
    """Шукає числа в рядку, склеюючи цілі та копійки, якщо вони розбиті комою"""
    full_line = "|".join(row_list).replace('"', '')
    # Шукаємо шаблони типу 43|0000 або 43.0000
    found = re.findall(r'(\d+)[|.](\d+)', full_line)
    if len(found) >= 2:
        buy = f"{found[0][0]}.{found[0][1][:2]}"
        sale = f"{found[1][0]}.{found[1][1][:2]}"
        return float(buy), float(sale)
    return None, None

def parse_currency():
    raw_data = get_raw_data(URL_CURRENCY_TABLE)
    if not raw_data: return "❌ Таблиця недоступна"
    
    rows = list(csv.reader(io.StringIO(raw_data)))
    res = {"USD": "немає даних", "EUR": "немає даних"}
    vals = {"USD": 0.0, "EUR": 0.0}

    for i, row in enumerate(rows):
        if not row: continue
        tag = row[0].strip().upper()
        
        # Якщо в колонці A написано USD або EUR, дані зазвичай рядком ВИЩЕ (згідно з твоїм скріншотом)
        if tag in ["USD", "EUR"]:
            # Спробуємо взяти числа з поточного рядка, а якщо їх там нема — з попереднього
            b, s = extract_nums(row)
            if b is None and i > 0:
                b, s = extract_nums(rows[i-1])
            
            if b:
                res[tag] = f"{b} / {s}"
                vals[tag] = b

    cross = round(vals["EUR"] / vals["USD"], 3) if vals["USD"] > 0 else "немає даних"

    return (
        f"🇺🇸 **USD:** {res['USD']}\n"
        f"🇪🇺 **EUR:** {res['EUR']}\n"
        f"💱 **Крос-курс EUR/USD:** {cross}"
    )

def get_weather():
    api_key = os.getenv('WEATHER_API_KEY')
    locs = [("Головецько", "lat=49.20&lon=23.45"), ("Львів", "q=Lviv")]
    reports = []
    for name, p in locs:
        url = f"http://api.openweathermap.org/data/2.5/weather?{p}&appid={api_key}&units=metric&lang=uk"
        d = get_raw_data(url)
        if d:
            js = json.loads(d)
            reports.append(f"📍 {name}: {round(js['main']['temp'])}°C, {js['weather'][0]['description'].capitalize()}")
    return "\n".join(reports)

def get_git_info(file_name, search_key):
    url = f"https://raw.githubusercontent.com/savchinviktorm-create/my-daily-bot/main/{file_name}"
    data = get_raw_data(url)
    if data:
        for line in data.splitlines():
            # Очищаємо рядок від зайвих пробілів для точного пошуку
            if search_key.lower() in line.lower():
                return line.split('—', 1)[-1].strip() if '—' in line else line.split(':', 1)[-1].strip()
    return "немає даних"

def send_report():
    token = os.getenv('TOKEN')
    chat_id = os.getenv('MY_CHAT_ID')
    now = datetime.now()
    
    months = ["січня", "лютого", "березня", "квітня", "травня", "червня", "липня", "серпня", "вересня", "жовтня", "листопада", "грудня"]
    day_month = f"{now.day} {months[now.month-1]}"
    
    msg = (
        f"📅 **РАНКОВИЙ ЗВІТ ({now.strftime('%d.%m.%Y')})**\n\n"
        f"🌡 **Погода:**\n{get_weather()}\n\n"
        f"💰 **Курс валют (Мінфін):**\n{parse_currency()}\n\n"
        f"😇 **Іменини:**\n{now.strftime('%d.%m')}: {get_git_info('names.txt', day_month)}\n\n"
        f"📜 **Історія:**\n{get_git_info('history.txt', now.strftime('%m-%d'))}\n\n"
        f"✨ **Гороскоп:**\n"
        f"♈ Овен: Будьте обережні з фінансами.\n♉ Телець: Зосередьтесь на головному.\n"
        f"♊ Близнюки: Час для відпочинку.\n♋ Рак: Слухайте інтуїцію.\n"
        f"♌ Лев: Вдалий день для починань.\n♍ Діва: Зверніть увагу на деталі.\n"
        f"♎ Терези: Гармонія у всьому.\n♏ Скорпіон: Енергійний день.\n"
        f"♐ Стрілець: Нові можливості.\n♑ Козоріг: Стійкість принесе успіх.\n"
        f"♒ Водолій: Час для креативу.\n♓ Риби: День для роздумів.\n\n"
        f"💡 **Цитата дня:**\n\"Хтось сидить у тіні сьогодні, тому що хтось давно посадив дерево.\" (Воррен Баффет)\n\n"
        f"😂 **Анекдот:**\n— Василю Івановичу, поїхали до міста, там виставка голографії йде!\n— Ні, Петько, на біса мені на голих графів дивитися?\n\n"
        f"🎄 До Нового року: {(datetime(now.year + 1, 1, 1) - now).days} днів!\n\n"
        f"⛽ **Ціни на пальне:**\nА-95: 56.15 грн\nДП: 52.30 грн\nГаз: 27.85 грн"
    )

    req = urllib.request.Request(f"https://api.telegram.org/bot{token}/sendMessage", 
                                 data=json.dumps({"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"}).encode('utf-8'),
                                 headers={'Content-Type': 'application/json'})
    urllib.request.urlopen(req)

if __name__ == "__main__":
    send_report()
