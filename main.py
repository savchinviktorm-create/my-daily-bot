import os
import urllib.request
import json
import re
from datetime import datetime

# --- ВСТАВ СВОЄ ПОСИЛАННЯ (CSV) ТУТ ---
URL_CURRENCY_TABLE = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSExxHF9GN-lpJF9I3L9kLzFoH9lo4_emwtiEoHpiezlf3ESOw6dxGrjmQwk1wuFC6mV6035wu6-l4M/pub?gid=2060076239&single=true&output=csv"

def get_raw_data(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as response:
            return response.read().decode('utf-8')
    except: return None

def parse_currency():
    data = get_raw_data(URL_CURRENCY_TABLE)
    if not data: return "❌ Не вдалося завантажити дані"
    
    lines = data.splitlines()
    usd_res, eur_res = "немає даних", "немає даних"
    usd_buy = 1.0 # для крос-курсу

    try:
        for line in lines:
            # Очищаємо рядок від зайвих лапок
            clean_line = line.replace('"', '')
            
            # Шукаємо USD
            if clean_line.startswith("USD"):
                # Знаходимо всі числа (цілі або дробові)
                nums = re.findall(r'\d+[.,]\d+|\d+', clean_line)
                if len(nums) >= 2:
                    # nums[0] - купівля, nums[-1] або nums[1] - продаж
                    b = nums[0].replace(',', '.')
                    s = nums[1].replace(',', '.')
                    usd_buy = float(b)
                    usd_res = f"{b} / {s}"
            
            # Шукаємо EUR
            if clean_line.startswith("EUR"):
                nums = re.findall(r'\d+[.,]\d+|\d+', clean_line)
                if len(nums) >= 2:
                    eb = nums[0].replace(',', '.')
                    es = nums[1].replace(',', '.')
                    eur_buy = float(eb)
                    eur_res = f"{eb} / {es}"

        # Рахуємо крос-курс
        try:
            cross = round(eur_buy / usd_buy, 3)
        except: cross = "немає даних"

        return (
            f"🇺🇸 **USD:** {usd_res}\n"
            f"🇪🇺 **EUR:** {eur_res}\n"
            f"💱 **Крос-курс EUR/USD:** {cross}"
        )
    except Exception as e:
        return f"⚠️ Помилка структури: {str(e)}"

def get_weather():
    api_key = os.getenv('WEATHER_API_KEY')
    locs = [("Головецько", "lat=49.20&lon=23.45"), ("Львів", "q=Lviv")]
    reports = []
    for name, p in locs:
        url = f"http://api.openweathermap.org/data/2.5/weather?{p}&appid={api_key}&units=metric&lang=uk"
        d = get_raw_data(url)
        if d:
            js = json.loads(d)
            temp = round(js['main']['temp'])
            desc = js['weather'][0]['description'].capitalize()
            reports.append(f"📍 {name}: {temp}°C, {desc}")
    return "\n".join(reports)

def get_git_info(file_name, search_key):
    url = f"https://raw.githubusercontent.com/savchinviktorm-create/my-daily-bot/main/{file_name}"
    data = get_raw_data(url)
    if data:
        for line in data.splitlines():
            if search_key in line:
                return line.split('—', 1)[-1].strip() if '—' in line else line.split(':', 1)[-1].strip()
    return "немає даних"

def send_report():
    token = os.getenv('TOKEN')
    chat_id = os.getenv('MY_CHAT_ID')
    now = datetime.now()
    
    # Дата для іменин
    months = ["січня", "лютого", "березня", "квітня", "травня", "червня", "липня", "серпня", "вересня", "жовтня", "листопада", "грудня"]
    day_month_text = f"{now.day} {months[now.month-1]}"
    
    history = get_git_info("history.txt", now.strftime("%m-%d"))
    names = get_git_info("names.txt", day_month_text)

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
