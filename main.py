import requests
from bs4 import BeautifulSoup
import telebot
import time
import random
from datetime import datetime
import pytz
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler

# --- НАЛАШТУВАННЯ ---
TOKEN = '8779933996:AAFtTmrPZ3qME5WV3ZRf7rfOHKzxbCsmSFY' 
CHAT_ID = '653398188'
TIMEZONE = pytz.timezone('Europe/Kyiv')

bot = telebot.TeleBot(TOKEN)

# --- "ХИТРІСТЬ" ДЛЯ RENDER (ЩОБ НЕ ВИМИКАВСЯ) ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")

def run_health_check():
    server = HTTPServer(('0.0.0.0', 10000), HealthCheckHandler)
    server.serve_forever()

# Запускаємо "міні-сайт" у фоні
Thread(target=run_health_check, daemon=True).start()

# --- ФУНКЦІЇ БОТА ---
def get_days_to_ny():
    now = datetime.now(TIMEZONE)
    ny = datetime(now.year + 1, 1, 1, tzinfo=TIMEZONE)
    return (ny - now).days

def get_weather():
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        r = requests.get('https://sinoptik.ua/pohoda/holovetsko', headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        t_min = soup.select_one('.temperature .min span').text
        t_max = soup.select_one('.temperature .max span').text
        return f"🌡 **Головецько:** {t_min}..{t_max}"
    except:
        return "🌡 **Погода:** Повітря свіже, настрій чудовий!"

def send_morning_report():
    days = get_days_to_ny()
    weather = get_weather()
    # Анекдот (випадковий з невеликого списку для стабільності)
    jokes = [
        "— Куме, а що ви будете робити на Новий Рік?\n— Та як завжди, обличчям в олів'є!",
        "Оптиміст вірить, що 2026-й буде кращим. Реаліст просто купив генератор.",
        "Ранок у Головецько: пташки співають, курс долара стабільний (високий)."
    ]
    msg = (f"Доброго ранку! ☀️\n\n"
           f"🎄 До Нового року: **{days}** днів\n\n"
           f"{weather}\n\n"
           f"💰 **Курс:** USD 42.80 / 43.40\n\n"
           f"😂 **Анекдот:**\n{random.choice(jokes)}")
    bot.send_message(CHAT_ID, msg, parse_mode='Markdown')

# Відправка відразу при старті
try:
    send_morning_report()
    print("Бот успішно запустився!")
except:
    pass

while True:
    now = datetime.now(TIMEZONE)
    current_time = now.strftime("%H:%M")

    if current_time == "08:20":
        send_morning_report()
        time.sleep(65)
    
    if current_time == "15:00":
        bot.send_message(CHAT_ID, f"🌤 Обідній звіт:\n\n{get_weather()}")
        time.sleep(65)

    time.sleep(30)
