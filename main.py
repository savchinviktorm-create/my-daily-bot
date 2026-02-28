import requests
import random
import datetime
import os
import pytz

# --- КРОК 3: НАЛАШТУВАННЯ (БЕРУТЬСЯ З GITHUB SECRETS) ---
# Ми використовуємо os.environ.get, щоб GitHub міг передати токен та ID каналу в код
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
TMDB_API_KEY = "583e99233cb332aaf8ab0ded7a92dde7"

KIEV_TZ = pytz.timezone('Europe/Kiev')

def get_now():
    return datetime.datetime.now(KIEV_TZ)

def send_telegram(text, photo_path=None):
    if photo_path and os.path.exists(photo_path):
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
        with open(photo_path, 'rb') as photo:
            payload = {"chat_id": TELEGRAM_CHAT_ID, "caption": text, "parse_mode": "HTML"}
            # Використовуємо files для відправки фото
            files = {"photo": photo}
            r = requests.post(url, data=payload, files=files)
    else:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"}
        r = requests.post(url, json=payload)
    return r.json()

def get_currency_logic():
    res = "💰 <b>КУРС ВАЛЮТ (Середній)</b>\n"
    try:
        # ПриватБанк
        p = requests.get("https://api.privatbank.ua/p24api/pubinfo?exchange&json&coursid=11", timeout=10).json()
        usd_p = next(i for i in p if i['ccy'] == 'USD')
        eur_p = next(i for i in p if i['ccy'] == 'EUR')
        
        # Монобанк
        m = requests.get("https://api.monobank.ua/bank/currency", timeout=10).json()
        usd_m = next(i for i in m if i['currencyCodeA'] == 840 and i['currencyCodeB'] == 980)
        eur_m = next(i for i in m if i['currencyCodeA'] == 978 and i['currencyCodeB'] == 980)
        
        # Середні показники
        avg_usd_buy = (float(usd_p['buy']) + float(usd_m['rateBuy'])) / 2
        avg_usd_sale = (float(usd_p['sale']) + float(usd_m['rateSell'])) / 2
        avg_eur_buy = (float(eur_p['buy']) + float(eur_m['rateBuy'])) / 2
        avg_eur_sale = (float(eur_p['sale']) + float(eur_m['rateSell'])) / 2
        
        cross_rate = avg_usd_sale / avg_eur_sale
        
        res += f"🇺🇸 USD: {avg_usd_buy:.2f}/{avg_usd_sale:.2f}\n"
        res += f"🇪🇺 EUR: {avg_eur_buy:.2f}/{avg_eur_sale:.2f}\n"
        res += f"⚖️ Крос-курс (USD/EUR): {cross_rate:.3f}\n"
        res += f"🏦 Приват: {usd_p['sale'][:5]} / 🐱 Моно: {usd_m['rateSell']}"
    except Exception:
        res += "⚠️ Курс тимчасово недоступний"
    return res

def get_random_image(folder):
    if not os.path.exists(folder): return None
    files = [f for f in os.listdir(folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    return os.path.join(folder, random.choice(files)) if files else None

def get_data_by_date(filename):
    try:
        today_str = get_now().strftime("%m-%d")
        if not os.path.exists(filename): return "Дані оновлюються"
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith(today_str):
                    return line[6:].strip()
        return "Дані оновлюються"
    except: return "Помилка файлу"

def get_random_lines(filename, count=1):
    try:
        if not os.path.exists(filename): return ["Дані відсутні"]
        with open(filename, 'r', encoding='utf-8') as f:
            lines = [l.strip() for l in f.readlines() if l.strip()]
        return random.sample(lines, min(len(lines), count)) if lines else ["Дані відсутні"]
    except: return ["Помилка"]

def days_to_ny():
    today = get_now().date()
    ny = datetime.date(today.year + 1, 1, 1)
    return (ny - today).days

def get_movie():
    try:
        page = random.randint(1, 10)
        url = f"https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}&language=uk-UA&page={page}"
        r = requests.get(url, timeout=10).json()
        m = random.choice(r['results
