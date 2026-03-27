import requests
import random
import datetime
import os
import pytz
import time

# --- НАЛАШТУВАННЯ ---
TMDB_API_KEY = os.environ.get("TMDB_API_KEY", "583e99233cb332aaf8ab0ded7a92dde7")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "8779933996:AAFtTmrPZ3qME5WV3ZRf7rfOHKzxbCsmSFY")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "653398188")
VIBER_TOKEN = os.environ.get("VIBER_TOKEN", "564974a12af0ed30-dbbbbb3694b529d4-5a27e9e2272c8279")
KIEV_TZ = pytz.timezone('Europe/Kiev')

def get_now():
    return datetime.datetime.now(KIEV_TZ)

# --- ТЕЛЕГРАМ (ЗАКОМЕНТОВАНО) ---
# def send_telegram(text, photo_path=None):
#     url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/send{'Photo' if photo_path else 'Message'}"
#     payload = {"chat_id": TELEGRAM_CHAT_ID, "caption" if photo_path else "text": text, "parse_mode": "HTML"}
#     if photo_path and os.path.exists(photo_path):
#         with open(photo_path, 'rb') as photo:
#             return requests.post(url, data=payload, files={"photo": photo}).json()
#     return requests.post(url, json=payload).json()

# --- ФУНКЦІЯ: Відправка у Viber (ВАРІАНТ 1 + 4: SILENT & SPLIT) ---
def send_viber(text, photo_path=None):
    if not VIBER_TOKEN:
        return {"error": "Немає токена"}
    
    headers = {"X-Viber-Auth-Token": VIBER_TOKEN}
    
    # 1. Отримуємо інфо
    try:
        info_res = requests.post("https://chatapi.viber.com/pa/get_account_info", json={}, headers=headers).json()
        if not info_res.get("webhook"):
            wh_payload = {"url": "https://postman-echo.com/post", "event_types": []}
            requests.post("https://chatapi.viber.com/pa/set_webhook", json=wh_payload, headers=headers)
    except Exception as e:
        return {"error": f"Помилка інфо: {e}"}

    # 2. Шукаємо ID адміністратора
    admin_id = None
    if info_res.get("status") == 0 and info_res.get("members"):
        for member in info_res["members"]:
            if member.get("role") == "superadmin":
                admin_id = member.get("id")
                break
        if not admin_id:
            admin_id = info_res["members"][0]["id"]
            
    if not admin_id:
        return {"error": "Не знайдено ID адміністратора"}
        
    # 3. Очищаємо текст від HTML
    clean_text = text.replace("<b>", "").replace("</b>", "").replace("<i>", "").replace("</i>", "")
    
    # --- ЛОГІКА РОЗПОДІЛУ ТЕКСТУ (ВАРІАНТ 4) ---
    VIBER_CAPTION_LIMIT = 1000 # Залишаємо запас від 1024
    part1 = clean_text
    part2 = None

    if len(clean_text) > VIBER_CAPTION_LIMIT:
        part1 = clean_text[:VIBER_CAPTION_LIMIT] + "..."
        part2 = " (продовження...)\n\n" + clean_text[VIBER_CAPTION_LIMIT:]

    # 4. Перевірка картинки
    photo_ready = False
    photo_url = ""
    if photo_path and os.path.exists(photo_path):
        repo = os.environ.get("GITHUB_REPOSITORY", "savchinviktorm-create/my-daily-bot")
        photo_url = f"https://raw.githubusercontent.com/{repo}/main/{photo_path.replace(os.sep, '/')}"
        
        for attempt in range(3):
            try:
                check = requests.head(photo_url, timeout=10)
                if check.status_code == 200:
                    photo_ready = True
                    break
            except: pass
            time.sleep(5)

    # 5. ВІДПРАВКА ПЕРШОЇ ЧАСТИНИ (Картинка + текст)
    if photo_ready:
        payload = {
            "from": admin_id,
            "type": "picture",
            "text": part1,
            "media": photo_url,
            "min_api_version": 7
        }
    else:
        payload = {
            "from": admin_id,
            "type": "text",
            "text": part1,
            "min_api_version": 7
        }
    
    main_res = requests.post("https://chatapi.viber.com/pa/post", json=payload, headers=headers).json()

    # 6. ВІДПРАВКА ДРУГОЇ ЧАСТИНИ (БЕЗ ЗВУКУ - ВАРІАНТ 1)
    if part2:
        time.sleep(1) # Невелика пауза, щоб повідомлення прийшли по порядку
        silent_payload = {
            "from": admin_id,
            "type": "text",
            "text": part2,
            "silent": True, # ТУТ МАГІЯ: БЕЗ ЗВУКУ
            "min_api_version": 7
        }
        requests.post("https://chatapi.viber.com/pa/post", json=silent_payload, headers=headers)

    return main_res

def get_currency_logic():
    res = "💰 <b>КУРС ВАЛЮТ</b>\n"
    try:
        nbu = requests.get("https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json", timeout=5).json()
        usd_nbu = next(i for i in nbu if i['cc'] == 'USD')
        eur_nbu = next(i for i in nbu if i['cc'] == 'EUR')
        res += f"🇺🇦 <b>НБУ:</b>\n└ USD: {usd_nbu['rate']:.2f} | EUR: {eur_nbu['rate']:.2f}\n"
    except: pass
    try:
        p = requests.get("https://api.privatbank.ua/p24api/pubinfo?exchange&json&coursid=11", timeout=5).json()
        usd_p = next(i for i in p if i['ccy'] == 'USD')
        eur_p = next(i for i in p if i['ccy'] == 'EUR')
        m = requests.get("https://api.monobank.ua/bank/currency", timeout=5).json()
        usd_m = next(i for i in m if i['currencyCodeA'] == 840 and i['currencyCodeB'] == 980)
        eur_m = next(i for i in m if i['currencyCodeA'] == 978 and i['currencyCodeB'] == 980)
        res += f"🏦 <b>ПриватБанк:</b>\n└ USD: {usd_p['buy'][:5]} / {usd_p['sale'][:5]} | EUR: {eur_p['buy'][:5]} / {eur_p['sale'][:5]}\n"
        res += f"🐾 <b>Монобанк:</b>\n└ USD: {usd_m['rateBuy']:.2f} / {usd_m['rateSell']:.2f} | EUR: {eur_m['rateBuy']:.2f} / {eur_m['rateSell']:.2f}\n"
    except: 
        res += "⚠️ Курс банків тимчасово недоступний\n"
    try:
        btc = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT", timeout=5).json()
        btc_price = float(btc['price'])
        res += f"₿ <b>Bitcoin (BTC):</b> {btc_price:,.0f} $\n".replace(',', ' ')
    except: pass
    return res.strip()

def get_data_by_date(filename):
    path = filename if os.path.exists(filename) else f"{filename}.txt"
    if not os.path.exists(path): return "Файл не знайдено"
    try:
        today_str = get_now().strftime("%m-%d")
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip().startswith(today_str):
                    content = line.strip()[5:].lstrip(' —-–:.').strip()
                    return content
        return "Дані відсутні"
    except: return "Помилка"

def get_random_lines(filename):
    path = filename if os.path.exists(filename) else f"{filename}.txt"
    if not os.path.exists(path): return "Дані оновлюються"
    try:
        with open(path, 'r', encoding='utf-8') as f:
            lines = [l.strip() for l in f.readlines() if l.strip()]
        return random.choice(lines) if lines else "Дані оновлюються"
    except: return "Помилка файлу"

def get_multiple_random_lines(filename, count=3):
    path = filename if os.path.exists(filename) else f"{filename}.txt"
    if not os.path.exists(path): return ["Дані оновлюються"]
    try:
        with open(path, 'r', encoding='utf-8') as f:
            lines = [l.strip() for l in f.readlines() if l.strip()]
        if not lines: return ["Дані оновлюються"]
        return random.sample(lines, min(count, len(lines)))
    except: return ["Помилка файлу"]

def get_random_image(folder):
    if not os.path.exists(folder): return None
    files = [f for f in os.listdir(folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    return os.path.join(folder, random.choice(files)) if files else None

def get_movie():
    try:
        page = random.randint(1, 10)
        url = f"https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}&language=uk-UA&page={page}"
        r = requests.get(url, timeout=10).json()
        m = random.choice(r['results'])
        return f"🎬 <b>ВЕЧІРНІЙ КІНОЗАЛ</b>\n🎥 <b>{m.get('title')}</b>\n⭐ Рейтинг: {m.get('vote_average')}\n🍿 {m.get('overview')[:200]}..."
    except: return "🎬 Час для кіно!"

def make_post():
    now = get_now()
    hour = now.hour
    weekday = now.weekday()
    divider = "✨ ✨ ✨ ✨ ✨"

    if weekday == 2 and hour == 16:
        img = get_random_image("media/books")
        return "📚 <b>КНИЖКОВА ПОЛИЦЯ</b>", img
    elif 5 <= hour < 11:
        img = get_random_image("media/morning")
        names = get_data_by_date('history')
        holidays = get_data_by_date('Holiday')
        history = get_data_by_date('Wiking')
        fact = get_random_lines('facts')
        text = (f"🌅 <b>ДОБРОГО РАНКУ!</b>\n"
                f"📅 Сьогодні: {now.strftime('%d.%m.%Y')}\n"
                f"{divider}\n"
                f"🎉 Свята: {holidays}\n"
                f"🎂 Іменини: {names}\n"
                f"📜 Історія: {history}\n"
                f"{divider}\n"
                f"{get_currency_logic()}\n"
                f"{divider}\n"
                f"🧠 Факт дня: {fact}")
        return text, img
    elif hour == 11:
        return "🗂 <b>КОРИСНА ПАМ'ЯТКА</b>", get_random_image("media/infographics")
    elif hour == 13:
        # Логіка 3-5 лайфхаків (Варіант без фото)
        advices = get_multiple_random_lines('advices', random.randint(3, 5))
        text = "💡 <b>ТОП ПОРАД НА СЬОГОДНІ:</b>\n\n"
        for i, a in enumerate(advices, 1):
            text += f"{i}. {a}\n\n"
        return text, None # Повертаємо None для фото, як домовлялися
    elif hour == 17:
        return f"📖 <b>ВЕЧІРНЯ ПРИТЧА</b>\n\n{get_random_lines('parables')}", get_random_image("media/parables")
    elif hour >= 20 or hour < 5:
        joke = get_random_lines('jokes')
        text = f"🌙 <b>ДОБРОЇ НОЧІ!</b>\n\n😂 Жарт: {joke}\n\n{get_movie()}"
        return text, get_random_image("media/evening")
    else:
        return "🛠 Технічний запуск", None

if __name__ == "__main__":
    content, photo = make_post()
    
    print("\n--- ЗАПУСК ПЕРЕВІРКИ VIBER ---")
    res_vb = send_viber(content, photo)
    print("ЛОГ Viber:", res_vb)
