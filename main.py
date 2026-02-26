import logging
import asyncio
import requests
import datetime
import random
import os
from flask import Flask
from threading import Thread
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# --- 1. ФЕЙКОВИЙ ВЕБ-СЕРВЕР ДЛЯ RENDER ---
app = Flask('')

@app.route('/')
def home():
    return "I'm alive!"

def run():
    # Render дає нам порт автоматично у змінну PORT
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- 2. НАЛАШТУВАННЯ БОТА ---
TOKEN = os.getenv("TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
MY_CHAT_ID = os.getenv("MY_CHAT_ID")

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()

def get_weather(city_name, lat, lon):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric&lang=uk"
    try:
        res = requests.get(url, timeout=10).json()
        if res.get("cod") != 200: return f"❌ {city_name}: Ключ ще активується..."
        temp = round(res['main']['temp'])
        return f"🌡 {city_name}: {'+' if temp > 0 else ''}{temp}°C, {res['weather'][0]['description'].capitalize()}"
    except: return f"❌ {city_name}: Помилка зв'язку"

async def build_report():
    now = datetime.datetime.now()
    w_gol = get_weather("с. Головецько", 49.1972, 23.4683)
    w_lviv = get_weather("м. Львів", 49.8397, 24.0297)
    return f"📅 **Звіт на {now.strftime('%d.%m.%Y')}**\n\n🌈 **ПОГОДА:**\n{w_gol}\n{w_lviv}"

async def send_daily():
    if MY_CHAT_ID:
        try:
            report = await build_report()
            await bot.send_message(chat_id=MY_CHAT_ID, text=report, parse_mode="Markdown")
        except Exception as e:
            logging.error(f"Error: {e}")

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer("✅ Бот ожив і прикидається сайтом! Тепер Render його не вб'є.")

async def main():
    # Запускаємо веб-сервер
    keep_alive()
    
    # Запускаємо планувальник
    scheduler = AsyncIOScheduler(timezone="Europe/Kiev")
    scheduler.add_job(send_daily, 'cron', hour=8, minute=0)
    scheduler.start()
    
    # Запускаємо бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
