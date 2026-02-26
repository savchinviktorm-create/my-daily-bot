import logging
import asyncio
import requests
import datetime
import random
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# --- ЧАСТИНА 1: ОБХІД ПОМИЛКИ RENDER (Фейковий сервер) ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive")

def run_health_server():
    port = int(os.getenv("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

# Запускаємо сервер у фоні, щоб Render не вимикав бота
threading.Thread(target=run_health_server, daemon=True).start()

# --- ЧАСТИНА 2: НАЛАШТУВАННЯ БОТА ---
TOKEN = os.getenv("TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
MY_CHAT_ID = os.getenv("MY_CHAT_ID")

LOCATIONS = {
    "с. Головецько": {"lat": 49.1972, "lon": 23.4683},
    "м. Львів": {"lat": 49.8397, "lon": 24.0297}
}

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- ЧАСТИНА 3: ФУНКЦІЇ ДАНИХ ---
def get_weather(city_name, lat, lon):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric&lang=uk"
    try:
        res = requests.get(url, timeout=10).json()
        if res.get("cod") != 200: 
            return f"❌ {city_name}: Ключ активується (зачекайте 1-2 год)"
        temp = round(res['main']['temp'])
        desc = res['weather'][0]['description'].capitalize()
        t_sign = "+" if temp > 0 else ""
        return f"🌡 {city_name}: {t_sign}{temp}°C, {desc}"
    except:
        return f"❌ {city_name}: Помилка зв'язку"

def get_currency():
    url = "https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=5"
    try:
        res = requests.get(url, timeout=10).json()
        usd = next(item for item in res if item["ccy"] == "USD")
        eur = next(item for item in res if item["ccy"] == "EUR")
        return (f"💵 **Курс (ПриватБанк):**\n"
                f"🇺🇸 USD: {float(usd['buy']):.2f} / {float(usd['sale']):.2f}\n"
                f"🇪🇺 EUR: {float(eur['buy']):.2f} / {float(eur['sale']):.2f}")
    except:
        return "❌ Курс валют недоступний"

def get_data_by_date(filename, current_date):
