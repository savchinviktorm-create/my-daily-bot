import os
import json
import urllib.request
import urllib.parse
from datetime import datetime

def send_telegram(token, chat_id, text):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    params = {'chat_id': chat_id, 'text': text, 'parse_mode': 'Markdown'}
    data = urllib.parse.urlencode(params).encode()
    req = urllib.request.Request(url, data=data)
    with urllib.request.urlopen(req) as f:
        return f.read().decode()

def get_weather(lat, lon, key):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={key}&units=metric&lang=uk"
    with urllib.request.urlopen(url) as f:
        data = json.loads(f.read().decode())
        temp = round(data['main']['temp'])
        desc = data['weather'][0]['description'].capitalize()
        return f"{'+' if temp > 0 else ''}{temp}°C, {desc}"

try:
    TOKEN = os.environ.get("TOKEN", "").strip()
    W_KEY = os.environ.get("WEATHER_API_KEY", "").strip()
    CHAT_ID = os.environ.get("MY_CHAT_ID", "").strip()

    report = f"📅 **Звіт на {datetime.now().strftime('%d.%m.%Y')}**\n\n"
    report += f"🌡 **Головецько**: {get_weather(49.19, 23.46, W_KEY)}\n"
    report += f"🌡 **Львів**: {get_weather(49.83, 24.02, W_KEY)}"

    print("Надсилаю звіт...")
    send_telegram(TOKEN, CHAT_ID, report)
    print("Успішно!")
except Exception as e:
    print(f"ПОМИЛКА: {e}")
    exit(1)
