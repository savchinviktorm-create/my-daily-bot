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

def clean_float(val):
    """Очищає текст і перетворює на число"""
    if not val: return 0.0
    clean = re.sub(r'[^\d.]', '', val.replace(',', '.'))
    try: return float(clean)
    except: return 0.0

def parse_currency():
    raw_data = get_raw_data(URL_CURRENCY_TABLE)
    if not raw_data: return "❌ Помилка завантаження"
    
    # Читаємо CSV і склеюємо всі рядки в один довгий список для пошуку
    rows = list(csv.reader(io.StringIO(raw_data)))
    all_data = []
    for r in rows: all_data.extend([c.strip() for c in r if c.strip()])

    usd_buy, usd_sale = 0.0, 0.0
    eur_buy, eur_sale = 0.0, 0.0

    # Шукаємо числа поруч із тегами USD та EUR
    for i, item in enumerate(all_data):
        if item == "USD":
            # У твоїй таблиці числа часто ПЕРЕД або ПІСЛЯ тега через розрив коми
            # Беремо кілька сусідніх елементів і шукаємо числа > 30
            nums = [clean_float(all_data[j]) for j in range(max(0, i-5), min(len(all_data), i+10)) if clean_float(all_data[j]) > 30]
            if len(nums) >= 2: usd_buy, usd_sale = nums[0], nums[1]
        
        if item == "EUR":
            nums = [clean_float(all_data[j]) for j in range(max(0, i-5), min(len(all_data), i+10)) if clean_float(all_data[j]) > 40]
            if len(nums) >= 2: eur_buy, eur_sale = nums[0], nums[1]

    if usd_buy == 0: return "⚠️ Дані в таблиці оновлюються (Мінфін недоступний)"

    cross = round(eur_buy / usd_buy, 3) if usd_buy > 0 else 0
    
    return (
        f"🇺🇸 **USD:** {usd_buy:.2f} / {usd_sale:.2f}\n"
        f"🇪🇺 **EUR:** {eur_buy:.2f} / {eur_sale:.2f}\n"
        f"💱 **Крос-курс (розрахунковий):** {cross}"
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
            if search_key.lower() in line.lower():
                return line.split('—', 1)[-1].strip() if '—' in line else line.split(':', 1)[-1].strip()
    return "немає даних"

def send_report():
    token = os.getenv('TOKEN')
    chat_id = os.getenv('MY_CHAT_ID')
    now = datetime.now()
    
    months = ["січня", "лютого", "березня", "квітня", "травня", "червня", "липня", "серпня", "вересня", "жовтня", "листопада", "грудня"]
    day_month = f"{now.day} {months[now.month-1]}" # Формує "27 лютого"
    
    history_key = now.strftime('%m-%d') # Формує "02-27"
    
    msg = (
        f"📅 **РАНКОВИЙ ЗВІТ ({now.strftime('%d.%m.%Y')})**\n\n"
        f"🌡 **Погода:**\n{get_weather()}\n\n"
        f"💰 **Курс валют:**\n{parse_currency()}\n\n"
        f"😇 **Іменини сьогодні:**\n{get_git_info('names.txt', day_month)}\n\n"
        f"📜 **Цей день в історії:**\n{get_git_info('history.txt', history_key)}\n\n"
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
