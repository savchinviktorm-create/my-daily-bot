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
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except:
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
        res = requests.get(url, timeout=10).json()
        temp = round(res["main"]["temp"])
        desc = res["weather"][0]["description"].capitalize()
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

    names_list = get_file_info("names.txt", date_key)
    history_note = get_file_info("history.txt", date_key)
    weather = get_weather()
    currency = get_currency()

    # Формування повідомлення (тільки якщо дані є)
    message_parts = [f"📅 **Сьогодні {date_display}**\n"]

    if names_list:
        message_parts.append(f"😇 **В цей день свої іменини святкують:**\n{names_list}\n\n✨ _Не забудь привітати близьких, якщо серед твого оточення є люди з такими іменами. Їм буде приємно!_")

    if history_note:
        message_parts.append(f"🕰 **Цей день в історії:**\n{history_note}")

    if weather or currency:
        meta_info = "--- \n"
        if weather:
            meta_info += f"🌤 **Погода:** {weather}\n"
        if currency:
            meta_info += f"💰 **Курс валют (НБУ):**\n{currency}"
        message_parts.append(meta_info)

    full_message = "\n\n".join(message_parts)

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID, 
        "text": full_message, 
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    requests.post(url, data=payload)

if __name__ == "__main__":
    send_message()
