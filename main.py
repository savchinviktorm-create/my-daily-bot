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
    # Головецько (через координати для точності) та Львів
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
            desc = data['weather'][0]['description']
            reports.append(f"📍 {loc['name']}: {temp}°C, {desc.capitalize()}")
    return "\n".join(reports) if reports else "Дані про погоду відсутні"

def get_currency():
    raw = get_data("https://api.privatbank.ua/p24api/pubinfo?exchange&json&coursid=11")
    if raw:
        data = json.loads(raw)
        res = []
        for c in data:
            if c['ccy'] in ['EUR', 'USD']:
                res.append(f"💵 {c['ccy']}: {round(float(c['buy']), 2)}/{round(float(c['sale']), 2)}")
        return "\n".join(sorted(res))
    return "Немає даних"

def get_history():
    today = datetime.now().strftime("%m-%d")
    url = "https://raw.githubusercontent.com/savchinviktorm-create/my-daily-bot/main/history.txt"
    data = get_data(url)
    if data:
        for line in data.splitlines():
            if line.startswith(today):
                return line.split(':', 1)[1].strip()
    return "27.02: день без подій"

def send_main():
    token = os.getenv('TOKEN')
    chat_id = os.getenv('MY_CHAT_ID')
    date_now = datetime.now().strftime("%d.%m.%Y")
    days_left = (datetime(datetime.now().year + 1, 1, 1) - datetime.now()).days

    message = (
        f"📅 **РАНКОВИЙ ЗВІТ ({date_now})**\n\n"
        f"🌡 **Погода:**\n{get_weather()}\n\n"
        f"💰 **Курс валют:**\n{get_currency()}\n\n"
        f"😇 **Іменини:**\n27.02: Кирило, Михайло, Федір\n\n"
        f"📜 **Історія:**\n{get_history()}\n\n"
        f"✨ **Гороскоп:**\n"
        f"♈ Овен: Будьте обережні з фінансами.\n♉ Телець: Зосередьтесь на головному.\n"
        f"♊ Близнюки: Час для відпочинку.\n♋ Рак: Слухайте інтуїцію.\n"
        f"♌ Лев: Вдалий день для починань.\n♍ Діва: Зверніть увагу на деталі.\n"
        f"♎ Терези: Гармонія у всьому.\n♏ Скорпіон: Енергійний день.\n"
        f"♐ Стрілець: Нові можливості.\n♑ Козоріг: Стійкість принесе успіх.\n"
        f"♒ Водолій: Час для креативу.\n♓ Риби: День для роздумів.\n\n"
        f"💡 **Цитата дня:**\n\"Хтось сидить у тіні сьогодні, тому що хтось давно посадив дерево.\" (Воррен Баффет)\n\n"
        f"😂 **Анекдот:**\n— Василю Івановичу, поїхали до міста, там виставка голографії йде!\n— Ні, Петько, на біса мені на голих графів дивитися?\n\n"
        f"🎄 До Нового року: {days_left} днів!\n\n"
        f"⛽ **Ціни на пальне:**\nА-95: 56.15 грн\nДП: 52.30 грн"
    )

    send_url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = json.dumps({"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}).encode('utf-8')
    req = urllib.request.Request(send_url, data=payload, headers={'Content-Type': 'application/json'})
    urllib.request.urlopen(req)

if __name__ == "__main__":
    send_main()
