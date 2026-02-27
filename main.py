import requests
import random
from datetime import datetime

# Дані підключення
TOKEN = "8779933996:AAFtTmrPZ3qME5WV3ZRf7rfOHKzxbCsmSFY"
CHAT_ID = "653398188"
# Пряме посилання на папку з картинками
GITHUB_MEDIA_BASE = "https://raw.githubusercontent.com/savchinviktorm-create/my-daily-bot/main/media/morning/"

def get_text_from_github(file_name, date_key):
    url = f"https://raw.githubusercontent.com/savchinviktorm-create/my-daily-bot/main/{file_name}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            for line in r.text.splitlines():
                if line.startswith(date_key):
                    return line[6:].strip()
    except: return None
    return None

def send_morning_post():
    now = datetime.now()
    date_key = now.strftime("%m-%d")
    
    # 1. Збір текстових даних
    names = get_text_from_github("names.txt", date_key)
    history = get_text_from_github("history.txt", date_key)
    days_to_ny = (datetime(now.year + 1, 1, 1) - now).days
    
    # 2. Курс валют
    try:
        cur = requests.get("https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json").json()
        usd = next(x for x in cur if x["cc"] == "USD")["rate"]
        currency = f"💵 <b>Курс валют:</b> USD {usd:.2f}"
    except: currency = ""

    # 3. Формування тексту (чистий стиль)
    message_parts = [f"☀️ <b>Доброго ранку! Сьогодні {now.strftime('%d.%m')}</b>"]
    if currency: message_parts.append(currency)
    if names: message_parts.append(f"😇 <b>День ангела:</b> {names}")
    if history: message_parts.append(f"🕰 <b>Цей день в історії:</b>\n{history}")
    message_parts.append(f"🎄 До Нового року: <b>{days_to_ny}</b> днів")
    
    full_text = "\n\n".join(message_parts)

    # 4. Вибір випадкової картинки (від 1 до 26)
    img_number = random.randint(1, 26)
    image_url = f"{GITHUB_MEDIA_BASE}{img_number}.png"

    # 5. Відправка фото з текстом
    url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
    payload = {
        "chat_id": CHAT_ID,
        "photo": image_url,
        "caption": full_text,
        "parse_mode": "HTML"
    }
    
    r = requests.post(url, data=payload)
    
    if r.status_code == 200:
        print(f"✅ Успішно надіслано пост із картинкою #{img_number}")
    else:
        # Якщо картинка не знайшлась, шлемо просто текст
        print(f"❌ Помилка медіа: {r.text}. Надсилаю текст.")
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                      data={"chat_id": CHAT_ID, "text": full_text, "parse_mode": "HTML"})

if __name__ == "__main__":
    send_morning_post()
