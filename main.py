import requests
import random
import datetime
import os
import pytz

# --- НАЛАШТУВАННЯ ---
TMDB_API_KEY = os.environ.get("TMDB_API_KEY", "583e99233cb332aaf8ab0ded7a92dde7")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "8779933996:AAFtTmrPZ3qME5WV3ZRf7rfOHKzxbCsmSFY")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "653398188")
VIBER_TOKEN = os.environ.get("VIBER_TOKEN", "564974a12af0ed30-dbbbbb3694b529d4-5a27e9e2272c8279")
KIEV_TZ = pytz.timezone('Europe/Kiev')

def get_now():
    return datetime.datetime.now(KIEV_TZ)

def send_telegram(text, photo_path=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/send{'Photo' if photo_path else 'Message'}"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "caption" if photo_path else "text": text, "parse_mode": "HTML"}
    if photo_path and os.path.exists(photo_path):
        with open(photo_path, 'rb') as photo:
            return requests.post(url, data=payload, files={"photo": photo}).json()
    return requests.post(url, json=payload).json()

# --- НОВА ФУНКЦІЯ: Відправка у Viber ---
def send_viber(text, photo_path=None):
    if not VIBER_TOKEN:
        return
    
    # Очищаємо текст від HTML тегів, бо Viber їх не підтримує
    clean_text = text.replace("<b>", "").replace("</b>", "").replace("<i>", "").replace("</i>", "")
    
    url = "https://chatapi.viber.com/pa/post"
    headers = {"X-Viber-Auth-Token": VIBER_TOKEN}
    
    if photo_path and os.path.exists(photo_path):
        # Формуємо публічне посилання на картинку з твого GitHub
        repo = os.environ.get("GITHUB_REPOSITORY", "savchinviktorm-create/my-daily-bot")
        photo_url = f"https://raw.githubusercontent.com/{repo}/main/{photo_path.replace(os.sep, '/')}"
        
        payload = {
            "from": {"name": "Простір"},
            "type": "picture",
            "text": clean_text,
            "media": photo_url
        }
    else:
        payload = {
            "from": {"name": "Простір"},
            "type": "text",
            "text": clean_text
        }
    
    try:
        return requests.post(url, json=payload, headers=headers).json()
    except Exception as e:
        return {"error": str(e)}

def get_currency_logic():
    res = "💰 <b>КУРС ВАЛЮТ</b>\n"
    
    # 1. НБУ (Нацбанк)
    try:
        nbu = requests.get("https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json", timeout=5).json()
        usd_nbu = next(i for i in nbu if i['cc'] == 'USD')
        eur_nbu = next(i for i in nbu if i['cc'] == 'EUR')
        res += f"🇺🇦 <b>НБУ:</b>\n└ USD: {usd_nbu['rate']:.2f} | EUR: {eur_nbu['rate']:.2f}\n"
    except: pass

    # 2. ПриватБанк та Монобанк
    try:
        p = requests.get("https://api.privatbank.ua/p24api/pubinfo?exchange&json&coursid=11", timeout=5).json()
        usd_p = next(i for i in p if i['ccy'] == 'USD')
        eur_p = next(i for i in p if i['ccy'] == 'EUR')
        m = requests.get("https://api.monobank.ua/bank/currency", timeout=5).json()
        usd_m = next(i for i in m if i['currencyCodeA'] == 840 and i['currencyCodeB'] == 980)
        eur_m = next(i for i in m if i['currencyCodeA'] == 978 and i['currencyCodeB'] == 980)
        res += f"🏦 <b>ПриватБанк:</b>\n└ USD: {usd_p['buy'][:5]} / {usd_p['sale'][:5]} | EUR: {eur_p['buy'][:5]} / {eur_p['sale'][:
