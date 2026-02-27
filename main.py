import requests
import os
from datetime import datetime

# Налаштування
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
CITY = "Kyiv"

def get_data(url):
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Помилка завантаження даних: {e}")
        return None

def get_file_info(file_name, search_key):
    url = f"https://raw.githubusercontent.com/savchinviktorm-create/my-daily-bot/main/{file_name}"
    data = get_data(url)
    if data:
        for line in data.splitlines():
            if line.startswith(search_key):
                content = line[6:].strip()
                return content if content else None
    return None

def get_weather():
    url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={WEATHER_API_KEY}&units=metric&lang=uk"
    try:
        res = requests.get(url, timeout=15).json()
        temp = round(res["main"]["temp"])
        desc = res["weather"][0]["description"].capitalize()
        return f"{temp}°C, {desc}"
    except:
        return None

def get_currency():
    url = "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json"
    try:
        res = requests.get(url, timeout=15).json()
        usd = next(item for item in res if item["cc"] == "USD")["rate"]
        eur = next(item for item in res if item["cc"] == "EUR")["rate"]
        return f"🇺🇸 USD: {usd:.2f} | 🇪🇺 EUR: {eur:.2f}"
    except:
        return None

def send_message():
    now = datetime.now()
    date_key = now.strftime("%m-%d")
    date_display = now.strftime("%d.%m.%Y")

    names_list = get_file_info("names.txt", date_key)
    history_note = get_file_info("history.txt", date_key)
    weather = get_weather()
    currency = get_currency()

    # Формування повідомлення через HTML (це надійніше за Markdown)
    message_parts = [f"📅 <b>Сьогодні {date_display}</b>\n"]

    if names_list:
        message_parts.append(
            f"😇 <b>В цей день свої іменини святкують:</b>\n{names_list}\n\n"
            f"✨ <i>Не забудь привітати близьких, якщо серед твого оточення є люди з такими іменами. Їм буде приємно!</i>"
        )

    if history_note:
        message_parts.append(f"🕰 <b>Цей день в історії:</b>\n{history_note}")

    if weather or currency:
        meta_info = "──────────────────\n"
        if weather:
            meta_info += f"🌤 <b>Погода:</b> {weather}\n"
        if currency:
            meta_info += f"💰 <b>Курс валют (НБУ):</b>\n{currency}"
        message_parts.append(meta_info)

    full_message = "\n\n".join(message_parts)

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID, 
        "text": full_message, 
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    
    # Виводимо результат у лог GitHub для діагностики
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        print("✅ Повідомлення успішно надіслано!")
    else:
        print(f"❌ Помилка Telegram: {response.status_code} - {response.text}")

if __name__ == "__main__":
    send_message()
