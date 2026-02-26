import logging
import asyncio
import requests
import datetime
import random
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Ключі з Environment
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
    mm_dd = now.strftime("%m-%d")
    w_gol = get_weather("с. Головецько", 49.1972, 23.4683)
    w_lviv = get_weather("м. Львів", 49.8397, 24.0297)
    return (
        f"📅 **Звіт на {now.strftime('%d.%m.%Y')}**\n\n"
        f"🌈 **ПОГОДА:**\n{w_gol}\n{w_lviv}\n\n"
        f"💡 **ЦИТАТА:**\n_{random.choice(['Дійте так, наче невдача неможлива.', 'Зміни – основа життя.'])}_\n\n"
        f"😂 **АНЕКДОТ:**\nСкоро все запрацює!"
    )

async def send_daily():
    if MY_CHAT_ID:
        report = await build_report()
        await bot.send_message(chat_id=MY_CHAT_ID, text=report, parse_mode="Markdown")

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer("✅ Бот на зв'язку! Тепер я працюю як 'Worker'. Чекай на звіт о 08:00.")

async def main():
    scheduler = AsyncIOScheduler(timezone="Europe/Kiev")
    scheduler.add_job(send_daily, 'cron', hour=8, minute=0)
    scheduler.start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
