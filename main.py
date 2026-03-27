import requests
import random
import datetime
import os
import pytz
import time  # ДОДАНО для затримок та перевірок

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

# --- ФУНКЦІЯ: Відправка у Viber (З РОЗУМНОЮ ПЕРЕВІРКОЮ ТА ФІКСОМ ID) ---
def send_viber(text, photo_path=None):
    if not VIBER_TOKEN:
        return {"error": "Немає токена"}
    
    headers = {"X-Viber-Auth-Token": VIBER_TOKEN}
    
    # 1. Отримуємо інфо та перевіряємо Webhook
    try:
        info_res = requests.post("https://chatapi.viber.com/pa/get_account_info", json={}, headers=headers).json()
        print(f"DEBUG Viber Info: {info_res}") # Щоб ми бачили структуру в логах
        
        if not info_res.get("webhook"):
            wh_payload = {"url": "https://postman-echo.com/post", "event_types": []}
            requests.post("https://chatapi.viber.com/pa/set_webhook", json=wh_payload, headers=headers)
    except Exception as e:
        return {"error": f"Помилка інфо: {e}"}

    # 2. Шукаємо ID адміністратора (Виправлено логіку)
    admin_id = None
    if info_res.get("status") == 0 and info_res.get("members"):
        for member in info_res["members"]:
            if member.get("role") == "superadmin":
                admin_id = member.get("id")
                break
        if not admin_id:
            admin_id = info_res["members"][0]["id"]
            
    if not admin_id:
        print("❌ ПОМИЛКА: Не знайдено ID адміністратора в списку members!")
        return {"error": "Не знайдено ID адміністратора"}
        
    # 3. Очищаємо текст від HTML
    clean_text = text.replace("<b>", "").replace("</b>", "").replace("<i>", "").replace("</i>", "")
    
    # 4. ПЕРЕВІРКА КАРТИНКИ НА АКТИВНІСТЬ (Smart Retry)
    photo_ready = False
    photo_url = ""
    
    if photo_path and os.path.exists(photo_path):
        repo = os.environ.get("GITHUB_REPOSITORY", "savchinviktorm-create/my-daily-bot")
        photo_url = f"https://raw.githubusercontent.com/{repo}/main/{photo_path.replace(os.sep, '/')}"
        
        print(f"--- Перевірка посилання: {photo_url} ---")
        for attempt in range(3):
            try:
                # Використовуємо HEAD, щоб не качати весь файл, а просто перевірити чи він є
                check = requests.head(photo_url, timeout=10)
                if check.status_code == 200:
                    print(f"✅ Картинка знайдена на GitHub (Спроба {attempt+1})")
                    photo_ready = True
                    break
                else:
                    print(f"⏳ Спроба {attempt+1}: Фото ще не прокинулося (Код {check.status_code})")
            except Exception as e:
                print(f"⏳ Спроба {attempt+1}: Помилка з'єднання ({e})")
            
            time.sleep(5) # Чекаємо 5 секунд між спробами

    # 5. Формування Payload з Fallback (якщо картинки немає — йде лише текст)
    if photo_ready:
        payload = {
            "from": admin_id,
            "type": "picture",
            "text": clean_text,
            "media": photo_url,
            "min_api_version": 7
        }
        print("🚀 Відправка як PICTURE")
    else:
        # Аварійний варіант: картинка не прогрузилася, шлемо текст, щоб пост не зник
        final_text = clean_text
        if photo_url:
            final_text += f"\n\n🖼 Фото до посту: {photo_url}"
            
        payload = {
            "from": admin_id,
            "type": "text",
            "text": final_text,
            "min_api_version": 7
        }
        print("⚠️ Відправка як TEXT (Fallback)")
    
    try:
        res = requests.post("https://chatapi.viber.com/pa/post", json=payload, headers=headers).json()
        return res
    except Exception as e:
        return {"error": str(e)}

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

def get_cinema_premieres():
    intros_cinema = [
        "🎟 <b>Новинки тижня в кіно:</b>", "🎬 <b>Прем'єрний четвер:</b>", "🍿 <b>Вже в кінотеатрах України:</b>", 
        "🎞 <b>Що подивитись на великому екрані:</b>", "🎬 <b>Свіжі прем'єри:</b>", "🎟 <b>Час у кіно:</b>", 
        "🎬 <b>Афіша тижня:</b>", "🍿 <b>Кіноновинки в Україні:</b>", "🎟 <b>Заплануй похід у кіно:</b>", 
        "🎬 <b>Гарячі прем'єри:</b>", "🎞 <b>Кіноафіша сьогодні:</b>", "🍿 <b>Прем'єри, які не можна пропустити:</b>", 
        "🎟 <b>Кіно на вихідні:</b>", "🎬 <b>Що нового в прокаті:</b>", "🎞 <b>Твій гід по кінотеатрах:</b>", 
        "🍿 <b>Український прокат сьогодні:</b>", "🎟 <b>Головні фільми тижня:</b>", "🎬 <b>Кінопрем'єри вже тут:</b>", 
        "🎞 <b>Дивись у кінотеатрах:</b>", "🍿 <b>Афіша на четвер:</b>", "🎟 <b>Кіносеанси тижня:</b>", 
        "🎬 <b>Новинки великого екрану:</b>", "🎞 <b>Сьогодні у прокаті:</b>", "🍿 <b>Попкорн та фільми:</b>", 
        "🎟 <b>Що зараз іде в кіно:</b>", "🎬 <b>Найцікавіші прем'єри:</b>", "🎞 <b>Топ новинок прокату:</b>", 
        "🍿 <b>День прем'єр в Україні:</b>", "🎟 <b>Твій квиток у кіносвіт:</b>", "🎬 <b>Старт прокату сьогодні:</b>"
    ]
    try:
        url = f"https://api.themoviedb.org/3/movie/now_playing?api_key={TMDB_API_KEY}&language=uk-UA&region=UA"
        r = requests.get(url, timeout=10).json()
        movies = r.get('results', [])[:5]
        if not movies: return "🎬 Сьогодні без гучних прем'єр."
        res = f"{random.choice(intros_cinema)}\n\n"
        for m in movies:
            title = m.get('title', 'Без назви')
            year = m.get('release_date', '----')[:4]
            desc = m.get('overview', 'Опис відсутній...')
            if len(desc) > 150: desc = desc[:147] + "..."
            res += f"🍿 <b>{title}</b> ({year})\n└ {desc}\n\n"
        return res
    except: return "🎬 Новинки кіно вже чекають на тебе!"

def make_post():
    now = get_now()
    hour = now.hour
    weekday = now.weekday()
    divider = "✨ ✨ ✨ ✨ ✨"

    congrats = ["Не забудьте привітати знайомих! 🥂", "Чудова нагода зателефонувати друзям! 🎈", "Надішліть їм тепле вітання! 🎁"] # (і так далі, твій список на місці)
    intros_advices = ["💡 <b>Корисний лайфхак:</b>", "🛠 <b>Спробуй це:</b>"] 
    # (Я скоротив списки для чату, але у твоєму файлі вони мають бути повними!)

    if weekday == 2 and hour == 16:
        img = get_random_image("media/books")
        text = f"📚 <b>КНИЖКОВА ПОЛИЦЯ</b>"
        return text, img
    elif 5 <= hour < 11:
        img = get_random_image("media/morning")
        text = f"🌅 <b>ДОБРОГО РАНКУ!</b>\n📅 Сьогодні: {now.strftime('%d.%m.%Y')}\n{divider}\n{get_currency_logic()}"
        return text, img
    elif hour == 11:
        return "🗂 <b>КОРИСНА ПАМ'ЯТКА</b>", get_random_image("media/infographics")
    elif hour == 13:
        return f"💡 <b>ПОРАДА:</b>\n{get_random_lines('advices')}", get_random_image("media/lifehacks")
    elif hour == 17:
        return f"📖 <b>ВЕЧІРНЯ ПРИТЧА</b>\n{get_random_lines('parables')}", get_random_image("media/parables")
    elif hour >= 20 or hour < 5:
        return f"🌙 <b>ДОБРОЇ НОЧІ!</b>\n{get_movie()}", get_random_image("media/evening")
    else:
        # Fallback для тестів
        return f"🛠 <b>Технічний тест Viber (бот на зв'язку).</b>\n💡 Порада: {get_random_lines('advices')}", get_random_image("media/infographics")

if __name__ == "__main__":
    content, photo = make_post()
    
    # ТЕЛЕГРАМ ЗАБЛОКОВАНО (Стоять решітки), ЩОБ НЕ СПАМИТИ
    # print("--- Відправка в Telegram ---")
    # res_tg = send_telegram(content, photo)
    # print("Результат Telegram:", res_tg)
    
    print("\n--- ЗАПУСК ТЕСТУ VIBER ---")
    res_vb = send_viber(content, photo)
    print("ЛОГ Viber:", res_vb)
