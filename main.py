import os
import asyncio
import logging
import requests
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# Налаштування (беруться з Environment Variables в Render)
TOKEN = os.getenv("TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
MY_CHAT_ID = os.getenv("MY_CHAT_ID")

bot = Bot(token=TOKEN)
dp = Dispatcher()

def get_weather(city_name, lat, lon):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric&lang=uk"
    try:
        res = requests.get(url, timeout=10).json()
        if res.get("cod") != 200: return f"❌ {city_name}: Помилка API"
        temp = round(res['main']['temp'])
        return f"🌡 {city_name}: {'+' if temp > 0 else ''}{temp}°C"
    except: return f"❌ {city_name}: Помилка зв'язку"

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer("Бот працює. Напиши /weather щоб перевірити погоду.")

@dp.message(Command("weather"))
async def weather_cmd(message: types.Message):
    w1 = get_weather("Головецько", 49.19, 23.46)
    w2 = get_weather("Львів", 49.83, 24.02)
    await message.answer(f"Погода на зараз:\n{w1}\n{w2}")

async def main():
    logging.basicConfig(level=logging.INFO)
    print("Бот запущений...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
