import os
import urllib.request
import json
from datetime import datetime

def get_data_from_url(url, is_json=True):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
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
    return "Інформація про події дня відсутня."

def get_weather():
    api_key = os.getenv('WEATHER_API_KEY')
    # Додано обидва міста: Головецько та Львів
    cities = {"Holovets'ko": "Головецько", "Lviv": "Львів"}
    res = []
    for eng, ukr in cities.items():
        data = get_data_from_url(f"http://api.openweathermap.org/data/2.5/weather?q={eng}&appid={api_key}&units=metric&lang=uk")
        if data:
            temp = round(data['main']['temp'])
            desc = data['weather'][0]['description']
            res.append(f"📍 {ukr}: {temp}°C, {desc}")
    return "\n".join(res) if res else "Дані про погоду недоступні"

def get_currency():
    data = get_data_from_url("https://api.privatbank.ua/p24api/pubinfo?exchange&json&coursid=11")
    if data:
        lines = []
        for c in data:
            if c['ccy'] in ['USD', 'EUR']:
                buy = round(float(c['buy']), 2)
                sale = round(float(c['sale']), 2)
                lines.append(f"💵 {c['ccy']}: {buy}/{sale}")
        return "\n".join(lines)
    return "Курс тимчасово недоступний"

def get_days_to_new_year():
    now = datetime.now()
    ny = datetime(now.year + 1, 1, 1)
    delta = ny - now
    return delta.days

def get_horoscope():
    # Повний список знаків для структури
    return (
        "♈ Овен: Будьте обережні з фінансами.\n"
        "♉ Телець: Зосередьтесь на головному.\n"
        "♊ Близнюки: Час для відпочинку.\n"
        "♋ Рак: Слухайте інтуїцію.\n"
        "♌ Лев: Вдалий день для починань.\n"
        "♍ Діва: Зверніть увагу на деталі.\n"
        "♎ Терези: Гармонія у всьому.\n"
        "♏ Скорпіон: Енергійний день.\n"
        "♐ Стрілець: Нові можливості.\n"
        "♑ Козоріг: Стійкість принесе успіх.\n"
        "♒ Водолій: Час для креативу.\n"
        "♓ Риби: День для роздумів."
    )

def send_full_report():
    token = os.getenv('TOKEN')
    chat_id = os.getenv('MY_CHAT_ID')
    date_str = datetime.now().strftime("%d.%m.%Y")
    
    message = (
        f"📅 **РАНКОВИЙ ЗВІТ ({date_str})**\n\n"
        f"🌡 **Погода:**\n{get_weather()}\n\n"
        f"💰 **Курс валют:**\n{get_currency()}\n\n"
        f"😇 **Іменини:**\n{datetime.now().strftime('%d.%m')}: Кирило, Михайло, Федір\n\n"
        f"📜 **Історія:**\n{get_history()}\n\n"
        f"✨ **Гороскоп:**\n{get_horoscope()}\n\n"
        f"💡 **Цитата дня:**\n\"Хтось сидить у тіні сьогодні, тому що хтось давно посадив дерево.\" (Воррен Баффет)\n\n"
        f"😂 **Анекдот:**\n— Василю Івановичу, поїхали до міста, там виставка голографії йде!\n— Ні, Петько, на біса мені на голих графів дивитися?\n\n"
        f"🎄 До Нового року: {get_days_to_new_year()} днів!\n\n"
        f"⛽ **Ціни на пальне:**\nА-95: 56.15 грн\nДП: 52.30 грн"
    )
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = json.dumps({"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}).encode('utf-8')
    req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})
    urllib.request.urlopen(req)

if __name__ == "__main__":
    send_full_report()
