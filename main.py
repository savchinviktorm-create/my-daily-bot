import requests
import random
import datetime
import os

# --- НАЛАШТУВАННЯ ТА КЛЮЧІ (З ТВОЇХ СКРІНШОТІВ) ---
TMDB_API_KEY = "583e99233cb332aaf8ab0ded7a92dde7"
HOLIDAY_API_KEY = "17904126938947f694726e6423985558"

# ВСТАВ СВОЇ ДАНІ ТУТ:
TELEGRAM_TOKEN = "ТВІЙ_ТОКЕН_БОТА"
TELEGRAM_CHAT_ID = "ТВІЙ_ID_ЧАТУ"

# --- ФУНКЦІЯ ВІДПРАВКИ ---
def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    try:
        r = requests.post(url, json=payload, timeout=10)
        print(f"Статус відправки: {r.status_code}")
        return r.json()
    except Exception as e:
        print(f"Помилка відправки: {e}")
        return None

# --- ГЕНЕРАТОР РОЗДІЛЮВАЧІВ ---
def get_divider():
    divs = [
        "\n━━━━━━━━━━━━━━━━━━━━━━\n",
        "\n✨ • • • • • • • • • • • ✨\n",
        "\n▬ ▬ ▬ ▬ ▬ ▬ ▬ ▬ ▬ ▬ ▬ ▬\n",
        "\n🔹 🔹 🔹 🔹 🔹 🔹 🔹 🔹 🔹 🔹\n",
        "\n──────────────────────\n",
        "\n◈━━━━━━━━━━━━━━━━━━━━◈\n"
    ]
    return random.choice(divs)

# --- ВАЛЮТА (ПРИВАТ + МОНО) ---
def get_full_currency():
    res = "💰 **КУРС ВАЛЮТ**\n"
    try:
        p = requests.get("https://api.privatbank.ua/p24api/pubinfo?exchange&json&coursid=11", timeout=5).json()
        u, e = next(i for i in p if i['ccy'] == 'USD'), next(i for i in p if i['ccy'] == 'EUR')
        res += f"🏦 Приват: 🇺🇸{u['buy'][:5]}/{u['sale'][:5]} | 🇪🇺{e['buy'][:5]}/{e['sale'][:5]}\n"
    except: res += "🏦 Приват: Недоступно\n"
    try:
        m = requests.get("
