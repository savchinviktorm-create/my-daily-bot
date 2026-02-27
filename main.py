import requests
import random
import io
from datetime import datetime
import pytz

# --- ТВОЇ ДАНІ ---
TOKEN = "8779933996:AAFtTmrPZ3qME5WV3ZRf7rfOHKzxbCsmSFY"
CHAT_ID = "653398188"
GITHUB_BASE = "https://raw.githubusercontent.com/savchinviktorm-create/my-daily-bot/main/"

def get_list_from_github(file_name):
    """Отримує всі рядки з файлу на GitHub"""
    try:
        r = requests.get(f"{GITHUB_BASE}{file_name}", timeout=10)
        if r.status_code == 200:
            return [line.strip() for line in r.text.splitlines() if line.strip()]
    except:
        return []
    return []

def send_morning_post():
    """Функція для ранкового поста (Панда + Валюта + Іменини)"""
    now = datetime.now(pytz.timezone('Europe/Kyiv'))
    date_key = now.strftime("%m-%d") # Формат 02-27
    
    # 1. Шукаємо іменини та історію
    names_list = get_list_from_github("names.txt")
    names = next((l[6:] for l in names_list if l.startswith(date_key)), "сьогодні немає даних")
    
    history_list = get_list_from_github("history.txt")
    history = next((l[6:] for l in history_list if l.startswith(date_key)), "цікавих подій не знайдено")

    # 2. Курс валют
    try:
        res = requests.get("https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json").json()
        usd = next(x for x in res if x["cc"] == "USD")["rate"]
        currency = f"💵 <b>Курс USD:</b> {usd:.2f} грн"
    except:
        currency = ""

    # 3. Текст поста
    text = f"☀️ <b>Доброго ранку! Сьогодні {now.strftime('%d.%m')}</b>\n\n"
    if currency: text += f"{currency}\n"
    text += f"😇 <b>День ангела:</b> {names}\n\n"
    text += f"🕰 <b>Цей день в історії:</b>\n{history}"

    # 4. Випадкова картинка (1-26)
    img_url = f"{GITHUB_BASE}media/morning/{random.randint(1, 26)}.png"
    
    try:
        img_data = requests.get(img_url).content
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendPhoto", 
                      files={"photo": ("image.png", img_data)}, 
                      data={"chat_id": CHAT_ID, "caption": text, "parse_mode": "HTML"})
        print("✅ Надіслано ранковий пост")
    except:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                      data={"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"})

def send_quote_post():
    """Функція для цитати дня"""
    quotes = get_list_from_github("quotes.txt")
    if not quotes:
        quotes = ["Кожен день — це нова можливість!"]
    
    quote = random.choice(quotes)
    emojis = ["✨", "🌟", "💡", "🚀", "💎", "🌈", "🔥", "🎯", "☀️", "🔋"]
    e1, e2 = random.sample(emojis, 2)
    
    text = f"{e1} <b>МОТИВАЦІЯ ДНЯ</b> {e1}\n\n«{quote}»\n\n{e2} <i>Бажаємо успіху!</i>"
    
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                  data={"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"})
    print("✅ Надіслано цитату")

if __name__ == "__main__":
    # Визначаємо поточну годину в Києві
    kyiv_tz = pytz.timezone('Europe/Kyiv')
    current_hour = datetime.now(kyiv_tz).hour

    # Логіка вибору поста
    if 5 <= current_hour <= 10:
        send_morning_post()
    else:
        send_quote_post()
