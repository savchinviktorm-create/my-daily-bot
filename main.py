import requests
import os
from datetime import datetime

# Налаштування
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
CITY = "Kyiv"

def clean_html(text):
    """Очищає текст від символів, які ламають Telegram HTML"""
    if not text:
        return ""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def get_data(url):
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        return r.text
    except:
        return None

def get_file_info(file_name, search_key):
    """Універсальний пошук по файлах на GitHub"""
    url = f"https://raw.githubusercontent.com/savchinviktorm-create/my-daily-bot/main/{file_name}"
    data = get_data(url)
    if data:
        for line in data.splitlines():
            if line.startswith(search_key):
                # Відрізаємо дату "MM-DD " (6 символів)
                return clean_html(line[6:].strip())
    return None

def get_weather():
    url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={WEATHER_API_KEY}&units=metric&lang=uk"
    try:
        res = requests.get(url, timeout=10).json()
        temp = round(res['main']['temp'])
        desc = res['weather'][0]['description'].capitalize()
        return f"{temp}°C, {desc}"
    except:
        return None

def get_currency():
    url = "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json"
    try:
        res = requests.get(url, timeout=10).json()
        usd = next(item for item in res if item["cc"] == "USD")["rate"]
        eur = next(item for item in res if item["cc"] == "EUR")["rate"]
        return f"🇺🇸 USD: {usd:.2f} | 🇪🇺 EUR: {eur:.2f}"
    except:
        return None

def send_message():
    now = datetime.now()
    date_key = now.strftime("%m-%d")
    date_display = now.strftime("%d.%m.%Y")

    names = get_file_info("names.txt", date_key)
    history = get_file_info("history.txt", date_key)
    weather = get_weather()
    currency = get_currency()

    # Складання повідомлення
    parts = [f"📅 <b>СЬОГОДНІ {date_display}</b>"]

    if names:
        parts.append(
            f"😇 <b>В цей день свої іменини святкують:</b>\n{names}\n\n"
            f"✨ <i>Не забудь привітати близьких, якщо серед твого оточення є люди з такими іменами. Їм буде приємно!</i>"
        )

    if history:
        parts.append(f"🕰 <b>Цей день в історії:</b>\n{history}")

    # Блок погоди та валют
    meta = []
    if weather:
        meta.append(f"🌤 <b>Погода:</b> {weather}")
    if currency:
        meta.append(f"💰 <b>Курс валют (НБУ):</b>\n{currency}")
    
    if meta:
        parts.append("──────────────────\n" + "\n".join(meta))

    full_text = "\n\n".join(parts)

    # Відправка
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": full_text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    
    r = requests.post(url, data=payload)
    
    if r.status_code == 200:
        print("✅ Успішно надіслано!")
    else:
        print(f"❌ Помилка Telegram: {r.status_code}")
        print(f"Відповідь сервера: {r.text}")

if __name__ == "__main__":
    send_message()
