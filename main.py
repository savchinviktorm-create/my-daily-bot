import os
import urllib.request
import json
from datetime import datetime

def get_data(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.read().decode('utf-8')
    except: return None

def get_weather():
    api_key = os.getenv('WEATHER_API_KEY')
    # Точні координати Головецько та Lviv
    locations = [
        {"name": "Головецько", "url": f"http://api.openweathermap.org/data/2.5/weather?lat=49.20&lon=23.45&appid={api_key}&units=metric&lang=uk"},
        {"name": "Львів", "url": f"http://api.openweathermap.org/data/2.5/weather?q=Lviv&appid={api_key}&units=metric&lang=uk"}
    ]
    reports = []
    for loc in locations:
        raw = get_data(loc['url'])
        if raw:
            data = json.loads(raw)
            temp = round(data['main']['temp'])
            desc = data['weather'][0]['description'].capitalize()
            reports.append(f"📍 {loc['name']}: {temp}°C, {desc}")
    return "\n".join(reports)

def get_file_info(file_name, search_key):
    url = f"https://raw.githubusercontent.com/savchinviktorm-create/my-daily-bot/main/{file_name}"
    data = get_data(url)
    if data:
        for line in data.splitlines():
            if search_key in line:
                return line.split('—', 1)[-1].strip() if '—' in line else line.split(':', 1)[-1].strip()
    return "немає даних"

def send_main():
    token = os.getenv('TOKEN')
    chat_id = os.getenv('MY_CHAT_ID')
    
    # Визначаємо дати
    now = datetime.now()
    date_str = now.strftime("%d.%m.%Y")
    day_month = now.strftime("%m-%d") # для history.txt
    
    # Форматуємо дату для names.txt (напр. "27 лютого")
    months_ukr = ["січня", "лютого", "березня", "квітня", "травня", "червня", 
                  "липня", "серпня", "вересня", "жовтня", "листопада", "грудня"]
    name_search = f"{now.day} {months_ukr[now.month-1]}"
    
    # Отримуємо дані з файлів
    history = get_file_info("history.txt", day_month)
    namenay = get_file_info("names.txt", name_search)
    
    # Курс валют
    raw_cur = get_data("https://api.privatbank.ua/p24api/pubinfo?exchange&json&coursid=11")
    cur_str = "Немає даних"
    if raw_cur:
        c_data = json.loads(raw_cur)
        cur_str = "\n".join([f"💵 {c['ccy']}: {round(float(c['buy']), 2)}/{round(float(c['sale']), 2)}" for c in c_data if c['ccy'] in ['EUR', 'USD']])

    message = (
        f"📅 **РАНКОВИЙ ЗВІТ ({date_str})**\n\n"
        f"🌡 **Погода:**\n{get_weather()}\n\n"
        f"💰 **Курс валют:**\n{cur_str}\n\n"
        f"😇 **Іменини:**\n{now.strftime('%d.%m')}: {namenay}\n\n"
        f"📜 **Історія:**\n{history}\n\n"
        f"✨ **Гороскоп:**\n"
        f"♈ Овен: Будьте обережні з фінансами.\n♉ Телець: Зосередьтесь на головному.\n"
        f" Gemini: Час для відпочинку.\n♋ Рак: Слухайте інтуїцію.\n"
        f"♌ Лев: Вдалий день для починань.\n♍ Діва: Зверніть увагу на деталі.\n"
        f"♎ Терези: Гармонія у всьому.\n♏ Скорпіон: Енергійний день.\n"
        f"♐ Стрілець: Нові можливості.\n♑ Козоріг: Стійкість принесе успіх.\n"
        f"♒ Водолій: Час для креативу.\n♓ Риби: День для роздумів.\n\n"
        f"💡 **Цитата дня:**\n\"Хтось сидить у тіні сьогодні, тому що хтось давно посадив дерево.\" (Воррен Баффет)\n\n"
        f"😂 **Анекдот:**\n— Василю Івановичу, поїхали до міста, там виставка голографії йде!\n— Ні, Петько, на біса мені на голих графів дивитися?\n\n"
        f"🎄 До Нового року: {(datetime(now.year + 1, 1, 1) - now).days} днів!\n\n"
        f"⛽ **Ціни на пальне:**\nА-95: 56.15 грн\nДП: 52.30 грн\nГаз: 27.85 грн"
    )

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = json.dumps({"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}).encode('utf-8')
    req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})
    urllib.request.urlopen(req)

if __name__ == "__main__":
    send_main()
