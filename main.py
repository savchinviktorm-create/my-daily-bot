import os
import urllib.request
import json
from datetime import datetime

def get_data_from_url(url):
    try:
        with urllib.request.urlopen(url) as response:
            return response.read().decode('utf-8')
    except:
        return None

def get_history_event():
    today = datetime.now().strftime("%m-%d")
    url = "https://raw.githubusercontent.com/savchinviktorm-create/my-daily-bot/main/history.txt"
    data = get_data_from_url(url)
    if data:
        for line in data.splitlines():
            if line.startswith(today):
                return line.split(':', 1)[1].strip()
    return "Сьогодні спокійний день у світовій історії."

def get_weather():
    # Використовуємо твій API ключ зі змінних середовища
    api_key = os.getenv('WEATHER_API_KEY')
    # Міста, які ти зазвичай відстежуєш
    cities = ["Holovets'ko", "Lviv"]
    weather_reports = []
    
    for city in cities:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=uk"
        try:
            with urllib.request.urlopen(url) as response:
                w_data = json.loads(response.read().decode('utf-8'))
                temp = round(w_data['main']['temp'])
                desc = w_data['weather'][0]['description']
                weather_reports.append(f"📍 {city}: {temp}°C, {desc.capitalize()}")
        except:
            continue
    return "\n".join(weather_reports) if weather_reports else "Дані про погоду тимчасово недоступні."

def send_full_report():
    token = os.getenv('TOKEN')
    chat_id = os.getenv('MY_CHAT_ID')
    
    date_now = datetime.now().strftime("%d.%m.%Y")
    history = get_history_event()
    weather = get_weather()
    
    # Створюємо повний текст повідомлення
    # Тут я додав структуру, яка була у тебе на скріншотах
    message_text = (
        f"📅 **ЗВІТ НА {date_now}**\n\n"
        f"🌡 **Погода:**\n{weather}\n\n"
        f"📜 **Цей день в історії:**\n{history}\n\n"
        f"✨ *Гарного дня та продуктивного настрою!*"
    )
    
    send_url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = json.dumps({
        "chat_id": chat_id,
        "text": message_text,
        "parse_mode": "Markdown"
    }).encode('utf-8')
    
    req = urllib.request.Request(send_url, data=payload, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as response:
        return response.getcode()

if __name__ == "__main__":
    send_full_report()
