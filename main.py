import requests
import os
from datetime import datetime

# Дані з секретів GitHub
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def get_from_github(file_name, date_key):
    """Просто бере текст із файлу на GitHub за датою"""
    url = f"https://raw.githubusercontent.com/savchinviktorm-create/my-daily-bot/main/{file_name}"
    try:
        r = requests.get(url)
        if r.status_code == 200:
            for line in r.text.splitlines():
                if line.startswith(date_key):
                    return line[6:].strip()
    except:
        pass
    return None

def get_currency():
    """Курс валют НБУ"""
    try:
        res = requests.get("https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json").json()
        usd = next(item for item in res if item["cc"] == "USD")["rate"]
        eur = next(item for item in res if item["cc"] == "EUR")["rate"]
        return f"🇺🇸 USD: {usd:.2f} | 🇪🇺 EUR: {eur:.2f}"
    except:
        return "Курс тимчасово недоступний"

def get_joke_and_quote():
    """Анекдоти та цитати (зовнішні API)"""
    quote = "Ніколи не пізно бути тим, ким ти міг би бути." # Заглушка, якщо API ляже
    joke = "— Куме, а що таке реформа? — Це коли старі податки називають новими словами."
    return quote, joke

def send_daily_report():
    now = datetime.now()
    date_key = now.strftime("%m-%d")
    days_to_ny = (datetime(now.year + 1, 1, 1) - now).days

    # Збираємо дані
    names = get_from_github("names.txt", date_key)
    history = get_from_github("history.txt", date_key)
    currency = get_currency()
    quote, joke = get_joke_and_quote()

    # Формуємо текст блоками
    text = f"📅 <b>СЬОГОДНІ {now.strftime('%d.%m.%Y')}</b>\n\n"
    
    text += f"💰 <b>Курс валют:</b>\n{currency}\n\n"
    
    if names:
        text += f"😇 <b>Іменини:</b>\n{names}\n"
        text += "<i>Не забудь привітати іменинників!</i>\n\n"
        
    if history:
        text += f"🕰 <b>Цей день в історії:</b>\n{history}\n\n"
    
    text += f"📜 <b>Цитата дня:</b>\n{quote}\n\n"
    text += f"😆 <b>Анекдот:</b>\n{joke}\n\n"
    text += f"🎄 <b>До Нового року залишилось:</b> {days_to_ny} днів!"

    # Відправка
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"})

if __name__ == "__main__":
    send_daily_report()
