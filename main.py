import os
import json
import urllib.request
import urllib.parse
from datetime import datetime

def get_weather(lat, lon, key):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={key}&units=metric&lang=uk"
        with urllib.request.urlopen(url, timeout=10) as f:
            data = json.loads(f.read().decode())
            temp = round(data['main']['temp'])
            desc = data['weather'][0]['description'].capitalize()
            return f"{'+' if temp > 0 else ''}{temp}°C, {desc}"
    except Exception as e:
        return f"помилка погоди ({e})"

def send_telegram(token, chat_id, text):
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        # Використовуємо просту передачу без Markdown, щоб уникнути помилки 400
        params = {'chat_id': chat_id, 'text': text}
        data = urllib.parse.urlencode(params).encode()
        req = urllib.request.Request(url, data=data)
        with urllib.request.urlopen(req, timeout=10) as f:
            return True
    except Exception as e:
        print(f"Помилка відправки в Telegram: {e}")
        return False

if __name__ == "__main__":
    # Отримуємо секрети та чистимо їх від випадкових пробілів
    TOKEN = os.environ.get("TOKEN", "").strip()
    W_KEY = os.environ.get("WEATHER_API_KEY", "").strip()
    CHAT_ID = os.environ.get("MY_CHAT_ID", "").strip()

    # Формуємо текст
    date_str = datetime.now().strftime('%d.%m.%Y')
    report = f"ЗВІТ НА {date_str}\n\n"
    
    weather_gol = get_weather(49.19, 23.46, W_KEY)
    weather_lviv = get_weather(49.83, 24.02, W_KEY)
    
    report += f"📍 Головецько: {weather_gol}\n"
    report += f"📍 Львів: {weather_lviv}\n\n"
    report += "Бот працює стабільно! ✅"

    print("Спроба відправки звіту...")
    if send_telegram(TOKEN, CHAT_ID, report):
        print("УСПІХ: Повідомлення в черзі!")
    else:
        print("ФЕЙЛ: Повідомлення не пішло.")
        exit(1)
