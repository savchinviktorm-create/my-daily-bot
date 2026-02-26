import requests
from bs4 import BeautifulSoup
import telebot
import time
import random
from datetime import datetime
import pytz

# --- НАЛАШТУВАННЯ ---
TOKEN = '8779933996:AAFtTmrPZ3qME5WV3ZRf7rfOHKzxbCsmSFY' 
CHAT_ID = '653398188'
TIMEZONE = pytz.timezone('Europe/Kyiv')

bot = telebot.TeleBot(TOKEN)

def get_days_to_new_year():
    now = datetime.now(TIMEZONE)
    next_year = now.year + 1
    new_year = datetime(next_year, 1, 1, tzinfo=TIMEZONE)
    delta = new_year - now
    return delta.days

def get_weather():
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        r = requests.get('https://sinoptik.ua/pohoda/holovetsko', headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        t_min = soup.select_one('.temperature .min span').text
        t_max = soup.select_one('.temperature .max span').text
        desc = soup.select_one('.wDescription .description').text.strip()
        return f"🌡 **Погода у Головецько:** {t_min}..{t_max}\n{desc}"
    except:
        return "⚠️ Погода тимчасово недоступна"

def get_currency():
    try:
        r = requests.get('https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=5', timeout=10).json()
        usd = next(i for i in r if i['ccy'] == 'USD')
        eur = next(i for i in r if i['ccy'] == 'EUR')
        return f"💰 **USD:** {float(usd['buy']):.2f}/{float(usd['sale']):.2f} | **EUR:** {float(eur['buy']):.2f}/{float(eur['sale']):.2f}"
    except:
        return "⚠️ Курс валют недоступний"

def get_dynamic_content():
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    # Гороскоп (Парсинг з goroskop.i.ua)
    try:
        res = requests.get('https://goroskop.i.ua/aquarius/', headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        horo = "♒️ **Водолій:** " + soup.select_one('.description').text.strip().split('.')[0] + "."
    except:
        horo = "♒️ **Водолій:** Зірки радять бути уважними до дрібниць."

    # Анекдот (Парсинг випадкового анекдоту українською)
    try:
        res = requests.get('https://anekdot.com.ua/random/', headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        # Беремо перший абзац тексту анекдоту
        joke_text = soup.select_one('.entry-content p').text.strip()
        joke = f"😂 **Анекдот дня:**\n{joke_text}"
    except:
        joke = "😂 **Анекдот:** Сьогодні без жартів, гарного дня!Ха-ха 😊"

    # Цитата/Афоризм (Випадкова з бази, бо API українською немає)
    quotes = [
        "Найкращий спосіб передбачити майбутнє — створити його.",
        "Успіх не приходить до тих, хто чекає, а до тих, хто діє.",
        "Маленькі кроки сьогодні — великі результати завтра.",
        "Дисципліна — це міст між цілями та досягненнями.",
        "Твоя енергія сьогодні визначає твій результат завтра."
    ]
    quote = f"📜 **Афоризм:** {random.choice(quotes)}"
    
    return f"{horo}\n\n{joke}\n\n{quote}"

def send_morning():
    days_left = get_days_to_new_year()
    msg = (f"Доброго ранку! ☀️ (08:20)\n\n"
           f"🎄 До Нового року залишилося: **{days_left}** днів\n\n"
           f"{get_weather()}\n\n"
           f"{get_currency()}\n\n"
           f"{get_dynamic_content()}")
    bot.send_message(CHAT_ID, msg, parse_mode='Markdown')

def send_afternoon():
    msg = f"Добрий день! 🌤 (15:00)\n\n{get_weather()}\n\n{get_currency()}"
    bot.send_message(CHAT_ID, msg, parse_mode='Markdown')

print("Бот запущений і чекає на розклад (08:20 та 15:00)...")

while True:
    now = datetime.now(TIMEZONE)
    current_time = now.strftime("%H:%M")

    if current_time == "08:20":
        send_morning()
        time.sleep(65)
    
    if current_time == "15:00":
        send_afternoon()
        time.sleep(65)

    time.sleep(30)
