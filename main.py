import logging
import asyncio
import requests
import datetime
import random
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder

# 1. НАЛАШТУВАННЯ
# На Render додай змінні оточення TOKEN та WEATHER_API_KEY
TOKEN = os.getenv("TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

LOCATIONS = {
    "с. Головецько": {"lat": 49.1972, "lon": 23.4683},
    "м. Львів": {"lat": 49.8397, "lon": 24.0297}
}

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()

# 2. ФУНКЦІЇ ДЛЯ ДАНИХ
def get_weather(city_name, lat, lon):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric&lang=uk"
    try:
        res = requests.get(url, timeout=10).json()
        temp = round(res['main']['temp'])
        desc = res['weather'][0]['description'].capitalize()
        t_sign = "+" if temp > 0 else ""
        return f"🌡 {city_name}: {t_sign}{temp}°C, {desc}"
    except:
        return f"❌ Погода для {city_name} недоступна"

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
    try:
        if not os.path.exists(filename): return None
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith(current_date):
                    return line.split(':', 1)[1].strip()
    except: return None
    return None

def get_random_line(filename):
    try:
        if not os.path.exists(filename): return "Файл відсутній"
        with open(filename, 'r', encoding='utf-8') as f:
            lines = [l.strip() for l in f.readlines() if l.strip()]
            return random.choice(lines) if lines else "Дані порожні"
    except: return "Помилка файлу"

# 3. ЛОГІКА БОТА
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.button(text="☀️ Отримати ранковий звіт")
    await message.answer(f"Вітаю, {message.from_user.first_name}! 👋", 
                         reply_markup=builder.as_markup(resize_keyboard=True))

@dp.message(lambda message: message.text == "☀️ Отримати ранковий звіт")
async def send_report(message: types.Message):
    now = datetime.datetime.now()
    mm_dd = now.strftime("%m-%d")
    
    w_gol = get_weather("с. Головецько", LOCATIONS["с. Головецько"]["lat"], LOCATIONS["с. Головецько"]["lon"])
    w_lviv = get_weather("м. Львів", LOCATIONS["м. Львів"]["lat"], LOCATIONS["м. Львів"]["lon"])
    
    report = (
        f"📅 **Сьогодні: {now.strftime('%d.%m.%Y')}**\n"
        f"━━━━━━━━━━━━━━\n\n"
        f"🌈 **ПОГОДА:**\n{w_gol}\n{w_lviv}\n\n"
        f"{get_currency()}\n\n"
        f"⏳ **ЦЕЙ ДЕНЬ В ІСТОРІЇ:**\n{get_data_by_date('history.txt', mm_dd) or 'Немає подій'}\n\n"
        f"😇 **ІМЕНИНИ:**\n{get_data_by_date('names.txt', mm_dd) or 'Немає'}\n\n"
        f"💡 **ЦИТАТА:**\n_{get_random_line('database.txt')}_\n\n"
        f"😂 **АНЕКДОТ:**\n{get_random_line('jokes.txt')}"
    )
    await message.answer(report, parse_mode="Markdown")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
