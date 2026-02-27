import os
import urllib.request
import json
from datetime import datetime

def get_data_from_url(url, is_json=True):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            content = response.read().decode('utf-8')
            return json.loads(content) if is_json else content
    except:
        return None

def get_history():
    today = datetime.now().strftime("%m-%d")
    url = "https://raw.githubusercontent.com/savchinviktorm-create/my-daily-bot/main/history.txt"
    data = get_data_from_url(url, is_json=False)
    if data:
        for line in data.splitlines():
            if line.startswith(today):
                return line.split(':', 1)[1].strip()
    return "27.02: день без подій"

def get_weather():
    api_key = os.getenv('WEATHER_API_KEY')
    cities = ["Holovets'ko", "Lviv"]
    res = []
    for city in cities:
        data = get_data_from_url(f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=uk")
        if data:
            temp = round(data['main']['temp'])
            desc = data['weather'][0]['description'].capitalize()
            emoji = "📍"
            res.append(f"{emoji} {city}: {temp}°C, {desc}")
    return "\n".join(res)

def get_currency():
    data = get_data_from_url("https://api.privatbank.ua/p24api/pubinfo?exchange&json&coursid=11")
    if data:
        for c in data:
            if c['ccy'] == 'USD':
                buy = round(float(c['buy']), 2)
                sale = round(float(c['sale']), 2)
                return f"💵 USD: {buy}/{sale}"
    return "Немає даних"

def get_horoscope():
    # Спрощений гороскоп, як у тебе був у звіті
    signs = {
        "♈ Овен": "Будьте обережні з фінансами.", "♉ Телець": "Зосередьтесь на головному.",
        "♊ Близнюки": "Час для відпочинку.", "♋ Рак": "Будьте обережні з фінансами.",
        "♌ Лев": "Вдалий день для починань.", "♍ Діва": "Вдалий день для починань.",
        "♎ Терези": "Вдалий день для починань.", "♏ Скорпіон": "Час для відпочинку.",
        "♐ Стрілець": "Час для відпочинку.", "♑ Козоріг": "Вдалий день для починань.",
        "♒ Водолій": "Зосередьтесь на головному.", "♓ Риби": "Вдалий день для починань."
    }
    return "\n".join([f"{k}: {v}" for k, v in signs.items()])

def send_full_report():
    token = os.getenv('TOKEN')
    chat_id = os.getenv('MY_CHAT_ID')
    date_now = datetime.now().strftime("%d.%m.%Y")
    
    # Формуємо текст точно за твоєю структурою
    message = (
        f"📅 **РАНКОВИЙ ЗВІТ ({date_now})**\n\n"
        f"🌡 **Погода:**\n{get_weather()}\n\n"
        f"💰 **Курс валют:**\n{get_currency()}\n\n"
        f"😇 **Іменини:**\n{datetime.now().strftime('%d.%m')}: немає даних\n\n"
        f"📜 **Історія:**\n{get_history()}\n\n"
        f"✨ **Гороскоп:**\n{get_horoscope()}\n\n"
        f"💡 **Цитата:**\n\"Хтось сидить у тіні сьогодні, тому що хтось давно посадив дерево. (Воррен Баффет)\"\n\n"
        f"😂 **Анекдот:**\n— Василю Івановичу, поїхали до міста, там виставка голографії йде!\n— Ні, Петько, на біса мені на голих графів дивитися?\n\n"
        f"🎄 До Нового року: 307 днів!\n\n"
        f"⛽ **Ціни на пальне:**\nА-95: 56.15 грн"
    )
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = json.dumps({"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}).encode('utf-8')
    req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})
    urllib.request.urlopen(req)

if __name__ == "__main__":
    send_full_report()
