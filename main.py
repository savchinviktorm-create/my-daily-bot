import os
import requests
import datetime

# Функція для отримання погоди
def get_weather(city, lat, lon, key):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={key}&units=metric&lang=uk"
    try:
        r = requests.get(url, timeout=10).json()
        temp = round(r['main']['temp'])
        desc = r['weather'][0]['description'].capitalize()
        return f"🌡 **{city}**: {'+' if temp > 0 else ''}{temp}°C, {desc}"
    except:
        return f"❌ {city}: помилка зв'язку"

if __name__ == "__main__":
    # Отримуємо змінні з Secrets
    TOKEN = os.getenv("TOKEN")
    W_KEY = os.getenv("WEATHER_API_KEY")
    CHAT_ID = os.getenv("MY_CHAT_ID")
    
    # Формуємо звіт
    now = datetime.datetime.now()
    report = f"📅 **Звіт на {now.strftime('%d.%m.%Y')}**\n\n"
    report += get_weather("с. Головецько", 49.1972, 23.4683, W_KEY) + "\n"
    report += get_weather("м. Львів", 49.8397, 24.0297, W_KEY)
    
    # Пряма відправка в Telegram
    send_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(send_url, data={'chat_id': CHAT_ID, 'text': report, 'parse_mode': 'Markdown'})
    print("Звіт відправлено!")
