import os
import urllib.request
import json
import re
from datetime import datetime

# Пряме посилання на ваш CSV
URL_CURRENCY_TABLE = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSExxHF9GN-lpJF9I3L9kLzFoH9lo4_emwtiEoHpiezlf3ESOw6dxGrjmQwk1wuFC6mV6035wu6-l4M/pub?gid=2060076239&single=true&output=csv"

def get_raw_data(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as response:
            return response.read().decode('utf-8')
    except: return None

def parse_currency():
    raw_data = get_raw_data(URL_CURRENCY_TABLE)
    if not raw_data: return "❌ Помилка завантаження таблиці"
    
    lines = raw_data.splitlines()
    usd_res, eur_res = "немає даних", "немає даних"
    u_buy, e_buy = 0.0, 0.0

    try:
        for line in lines:
            # Прибираємо лапки та розбиваємо по комі
            parts = [p.strip().replace('"', '') for p in line.split(',')]
            # Фільтруємо лише непорожні елементи, які містять цифри або назву валюти
            content = [p for p in parts if p]
            
            if not content: continue

            # Шукаємо USD (зазвичай це рядок, де перше слово USD)
            if content[0] == "USD" and len(content) >= 3:
                # content[1] - ціла частина купівлі, content[2] - копійки купівлі
                # content[3] - ціла частина продажу, content[4] - копійки продажу
                u_buy_val = f"{content[1]}.{content[2][:2]}"
                u_sale_val = f"{content[3]}.{content[4][:2]}"
                u_buy = float(u_buy_val)
                usd_res = f"{u_buy_val} / {u_sale_val}"

            # Шукаємо EUR
            if content[0] == "EUR" and len(content) >= 3:
                e_buy_val = f"{content[1]}.{content[2][:2]}"
                e_sale_val = f"{content[3]}.{content[4][:2]}"
                e_buy = float(e_buy_val)
                eur_res = f"{e_buy_val} / {e_sale_val}"

        # Крос-курс
        cross = round(e_buy / u_buy, 3) if u_buy > 0 else "немає даних"

        return (
            f"🇺🇸 **USD:** {usd_res}\n"
            f"🇪🇺 **EUR:** {eur_res}\n"
            f"💱 **Крос-курс EUR/USD:** {cross}"
        )
    except Exception as e:
        return "⚠️ Дані в таблиці оновлюються..."

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
        lines = data.splitlines()
        for line in lines:
            if search_key.lower() in line.lower():
                return line.split('—', 1)[-1].strip() if '—' in line else line.split(':', 1)[-1].strip()
    return "немає даних"

def send_report():
    token = os.getenv('TOKEN')
    chat_id = os.getenv('MY_CHAT_ID')
    now = datetime.now()
    
    months = ["січня", "лютого", "березня", "квітня", "травня", "червня", "липня", "серпня", "вересня", "жовтня", "листопада", "грудня"]
    day_month = f"{now.day} {months[now.month-1]}"
    
    history = get_git_info('history.txt', now.strftime('%m-%d'))
    names = get_git_info('names.txt', day_month)

    msg = (
        f"📅 **РАНКОВИЙ ЗВІТ ({now.strftime('%d.%m.%Y')})**\n\n"
        f"🌡 **Погода:**\n{get_weather()}\n\n"
        f"💰 **Курс валют (Мінфін):**\n{parse_currency()}\n\n"
        f"😇 **Іменини:**\n{now.strftime('%d.%m')}: {names}\n\n"
        f"📜 **Історія:**\n{history}\n\n"
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
