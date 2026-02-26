import os
import requests
import datetime

def get_weather(city, lat, lon, key):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={key}&units=metric&lang=uk"
    try:
        r = requests.get(url).json()
        temp = round(r['main']['temp'])
        desc = r['weather'][0]['description']
        return f"🌡 {city}: {temp}°C, {desc}"
    except:
        return f"❌ {city}: помилка"

if __name__ == "__main__":
    TOKEN = os.getenv("TOKEN")
    W_KEY = os.getenv("WEATHER_API_KEY")
    CHAT_ID = os.getenv("MY_CHAT_ID")
    
    report = f"📅 Звіт на {datetime.datetime.now().strftime('%d.%m')}\n\n"
    report += get_weather("Головецько", 49.19, 23.46, W_KEY) + "\n"
    report += get_weather("Львів", 49.83, 24.02, W_KEY)
    
    # Відправка через простий запит без бібліотек
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={'chat_id': CHAT_ID, 'text': report, 'parse_mode': 'Markdown'})
