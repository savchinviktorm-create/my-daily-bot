import requests
import random
import datetime
import os
import pytz
import time
import re
import json
from urllib.parse import quote

# --- НАЛАШТУВАННЯ ---
TMDB_API_KEY = os.environ.get("TMDB_API_KEY", "583e99233cb332aaf8ab0ded7a92dde7")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "8779933996:AAFtTmrPZ3qME5WV3ZRf7rfOHKzxbCsmSFY")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "653398188")
VIBER_TOKEN = os.environ.get("VIBER_TOKEN", "564974a12af0ed30-dbbbbb3694b529d4-5a27e9e2272c8279")  # Твій токен додано сюди
MINI_APP_URL = os.environ.get("MINI_APP_URL", "https://t.me/ProstirKorBot/shchaslyvyi")  # Вкажіть тут посилання на ваш Mini App

try:
    KIEV_TZ = pytz.timezone('Europe/Kyiv')
except Exception:
    KIEV_TZ = pytz.timezone('Europe/Kiev')

def get_now():
    return datetime.datetime.now(KIEV_TZ)

def strip_html_for_viber(text):
    clean_text = re.sub(r'<[^>]+>', '', text)
    clean_text = clean_text.replace('&nbsp;', ' ').replace('&amp;', '&')
    return clean_text

def split_text_for_viber(text, max_len):
    if len(text) <= max_len:
        return [text]

    parts = []
    remaining = text

    while len(remaining) > max_len:
        split_at = remaining.rfind('\n', 0, max_len)
        if split_at == -1 or split_at < int(max_len * 0.6):
            split_at = remaining.rfind(' ', 0, max_len)
        if split_at == -1 or split_at < int(max_len * 0.6):
            split_at = max_len

        part = remaining[:split_at].rstrip()
        if not part:
            part = remaining[:max_len].rstrip()
            split_at = len(part)

        parts.append(part)
        remaining = remaining[split_at:].lstrip()

    if remaining:
        parts.append(remaining)

    return parts

def build_viber_media_url(photo_path):
    if not photo_path or not os.path.exists(photo_path):
        return ""

    repo = os.environ.get("GITHUB_REPOSITORY", "savchinviktorm-create/my-daily-bot")
    normalized_path = photo_path.replace('\\', '/').replace(os.sep, '/')
    encoded_path = quote(normalized_path, safe="/._-")
    return f"https://raw.githubusercontent.com/{repo}/main/{encoded_path}"

def check_viber_media(photo_url):
    if not photo_url:
        return False

    for attempt in range(3):
        try:
            check = requests.head(photo_url, timeout=10, allow_redirects=True)
            if check.status_code == 200:
                return True
        except Exception:
            pass

        try:
            check = requests.get(photo_url, timeout=15, stream=True)
            status_ok = check.status_code == 200
            check.close()
            if status_ok:
                return True
        except Exception:
            pass

        time.sleep(5)

    return False

def send_telegram(text, photo_path=None, reply_markup=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/send{'Photo' if photo_path else 'Message'}"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "caption" if photo_path else "text": text,
        "parse_mode": "HTML"
    }

    if photo_path and os.path.exists(photo_path):
        if reply_markup:
            payload["reply_markup"] = json.dumps(reply_markup)
        with open(photo_path, 'rb') as photo:
            return requests.post(url, data=payload, files={"photo": photo}).json()

    if reply_markup:
        payload["reply_markup"] = reply_markup

    return requests.post(url, json=payload).json()

# --- ФУНКЦІЯ: Відправка у Viber (ВАРІАНТ 1 + 4: SILENT & SPLIT + FALLBACK) ---
def send_viber(text, photo_path=None):
    if not VIBER_TOKEN:
        return {"error": "Немає токена"}

    headers = {"X-Viber-Auth-Token": VIBER_TOKEN}

    # 1. Отримуємо інфо
    try:
        info_res = requests.post(
            "https://chatapi.viber.com/pa/get_account_info",
            json={},
            headers=headers,
            timeout=20
        ).json()
        if not info_res.get("webhook"):
            wh_payload = {"url": "https://postman-echo.com/post", "event_types": []}
            requests.post(
                "https://chatapi.viber.com/pa/set_webhook",
                json=wh_payload,
                headers=headers,
                timeout=20
            )
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
    clean_text = strip_html_for_viber(text)

    # 4. Ліміти для Viber
    VIBER_TEXT_LIMIT = 7000
    VIBER_PICTURE_CAPTION_LIMIT = 768

    # 5. Перевірка картинки
    photo_ready = False
    photo_url = ""
    if photo_path and os.path.exists(photo_path):
        photo_url = build_viber_media_url(photo_path)
        photo_ready = check_viber_media(photo_url)

    # 6. Готуємо частини тексту
    if photo_ready:
        text_parts = split_text_for_viber(clean_text, VIBER_PICTURE_CAPTION_LIMIT)
    else:
        text_parts = split_text_for_viber(clean_text, VIBER_TEXT_LIMIT)

    main_res = None
    fallback_responses = []
    additional_parts_responses = []

    # 7. ВІДПРАВКА ПЕРШОЇ ЧАСТИНИ
    if photo_ready:
        payload = {
            "from": admin_id,
            "type": "picture",
            "text": text_parts[0],
            "media": photo_url,
            "min_api_version": 7
        }
        main_res = requests.post(
            "https://chatapi.viber.com/pa/post",
            json=payload,
            headers=headers,
            timeout=30
        ).json()

        # Якщо Viber відхилив фото — не втрачаємо пост, повторно відправляємо все текстом
        if main_res.get("status") != 0:
            text_only_parts = split_text_for_viber(clean_text, VIBER_TEXT_LIMIT)
            for idx, part in enumerate(text_only_parts):
                fallback_payload = {
                    "from": admin_id,
                    "type": "text",
                    "text": part,
                    "min_api_version": 7
                }
                if idx > 0:
                    fallback_payload["silent"] = True

                fallback_res = requests.post(
                    "https://chatapi.viber.com/pa/post",
                    json=fallback_payload,
                    headers=headers,
                    timeout=30
                ).json()
                fallback_responses.append(fallback_res)
                time.sleep(1)

            return {
                "main_response": main_res,
                "fallback_text_responses": fallback_responses
            }

        # Якщо перша частина з картинкою пройшла — надсилаємо решту тексту тихо
        if len(text_parts) > 1:
            for part in text_parts[1:]:
                time.sleep(1)
                silent_payload = {
                    "from": admin_id,
                    "type": "text",
                    "text": part,
                    "silent": True,
                    "min_api_version": 7
                }
                silent_res = requests.post(
                    "https://chatapi.viber.com/pa/post",
                    json=silent_payload,
                    headers=headers,
                    timeout=30
                ).json()
                additional_parts_responses.append(silent_res)

        return {
            "main_response": main_res,
            "additional_parts_responses": additional_parts_responses
        }

    else:
        # Якщо картинки немає або Viber не зміг її підтягнути — надсилаємо весь пост текстом
        for idx, part in enumerate(text_parts):
            payload = {
                "from": admin_id,
                "type": "text",
                "text": part,
                "min_api_version": 7
            }
            if idx > 0:
                payload["silent"] = True

            res = requests.post(
                "https://chatapi.viber.com/pa/post",
                json=payload,
                headers=headers,
                timeout=30
            ).json()

            if idx == 0:
                main_res = res
            else:
                additional_parts_responses.append(res)

            time.sleep(1)

        return {
            "main_response": main_res,
            "additional_parts_responses": additional_parts_responses
        }

def get_btc_price_text():
    # 1. Основний Binance
    try:
        btc = requests.get(
            "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT",
            timeout=5
        ).json()
        btc_price = float(btc["price"])
        return f"₿ <b>Bitcoin (BTC):</b> {btc_price:,.0f} $\n".replace(',', ' ')
    except:
        pass

    # 2. Binance market-data only
    try:
        btc = requests.get(
            "https://data-api.binance.vision/api/v3/ticker/price?symbol=BTCUSDT",
            timeout=5
        ).json()
        btc_price = float(btc["price"])
        return f"₿ <b>Bitcoin (BTC):</b> {btc_price:,.0f} $\n".replace(',', ' ')
    except:
        pass

    # 3. Запасний варіант — Bybit
    try:
        btc = requests.get(
            "https://api.bybit.com/v5/market/tickers?category=spot&symbol=BTCUSDT",
            timeout=5
        ).json()
        btc_price = float(btc["result"]["list"][0]["lastPrice"])
        return f"₿ <b>Bitcoin (BTC):</b> {btc_price:,.0f} $\n".replace(',', ' ')
    except:
        pass

    # Якщо ніде не вийшло — просто нічого не додаємо
    return ""

def get_currency_logic():
    res = "💰 <b>КУРС ВАЛЮТ</b>\n"
    
    # 1. НБУ (Нацбанк)
    try:
        nbu = requests.get("https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json", timeout=5).json()
        usd_nbu = next(i for i in nbu if i['cc'] == 'USD')
        eur_nbu = next(i for i in nbu if i['cc'] == 'EUR')
        res += f"🇺🇦 <b>НБУ:</b>\n└ USD: {usd_nbu['rate']:.2f} | EUR: {eur_nbu['rate']:.2f}\n"
    except:
        pass

    # 2. ПриватБанк та Монобанк
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

    # 3. Bitcoin — безпечне додавання
    btc_line = get_btc_price_text()
    if btc_line:
        res += btc_line

    return res.strip()

def get_data_by_date(filename):
    path = filename if os.path.exists(filename) else f"{filename}.txt"
    if not os.path.exists(path):
        return "Файл не знайдено"
    try:
        today_str = get_now().strftime("%m-%d")
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip().startswith(today_str):
                    content = line.strip()[5:].lstrip(' —-–:.').strip()
                    return content
        return "Дані відсутні"
    except:
        return "Помилка"

def get_random_lines(filename):
    path = filename if os.path.exists(filename) else f"{filename}.txt"
    if not os.path.exists(path):
        return "Дані оновлюються"
    try:
        with open(path, 'r', encoding='utf-8') as f:
            lines = [l.strip() for l in f.readlines() if l.strip()]
        return random.choice(lines) if lines else "Дані оновлюються"
    except:
        return "Помилка файлу"

def get_multiple_random_lines(filename, count=3):
    path = filename if os.path.exists(filename) else f"{filename}.txt"
    if not os.path.exists(path):
        return ["Дані оновлюються"]
    try:
        with open(path, 'r', encoding='utf-8') as f:
            lines = [l.strip() for l in f.readlines() if l.strip()]
        if not lines:
            return ["Дані оновлюються"]
        return random.sample(lines, min(count, len(lines)))
    except:
        return ["Помилка файлу"]

def get_random_image(folder):
    if not os.path.exists(folder):
        return None
    files = [f for f in os.listdir(folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    return os.path.join(folder, random.choice(files)) if files else None

def get_movie():
    try:
        page = random.randint(1, 10)
        url = f"https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}&language=uk-UA&page={page}"
        r = requests.get(url, timeout=10).json()
        m = random.choice(r['results'])
        return f"🎬 <b>ВЕЧІРНІЙ КІНОЗАЛ</b>\n🎥 <b>{m.get('title')}</b>\n⭐ Рейтинг: {m.get('vote_average')}\n🍿 {m.get('overview')[:200]}..."
    except:
        return "🎬 Час для кіно!"

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
        if not movies:
            return "🎬 Сьогодні без гучних прем'єр."
        res = f"{random.choice(intros_cinema)}\n\n"
        for m in movies:
            title = m.get('title', 'Без назви')
            year = m.get('release_date', '----')[:4]
            desc = m.get('overview', 'Опис відсутній...')
            if len(desc) > 150:
                desc = desc[:147] + "..."
            res += f"🍿 <b>{title}</b> ({year})\n└ {desc}\n\n"
        return res
    except:
        return "🎬 Новинки кіно вже чекають на тебе!"

def make_post():
    now = get_now()
    hour = now.hour
    weekday = now.weekday()
    divider = "✨ ✨ ✨ ✨ ✨"

    congrats = [
        "Не забудьте привітати знайомих! 🥂", "Чудова нагода зателефонувати друзям! 🎈", "Надішліть їм тепле вітання! 🎁",
        "Маленьке SMS зробить їхній день кращим! 💌", "Поділіться радістю з іменинниками! ✨", "Привітання зігріває серце. Напишіть їм! 😊",
        "Сьогодні гарний день для добрих слів! ☀️", "Встигніть побажати всього найкращого! 🎂", "Ангели радіють вашим вітанням! 👼",
        "Ваше привітання сьогодні дуже чекають! 🧸", "Не тримайте добро в собі — привітайте! 🕊", "Зробіть приємний сюрприз сьогодні! 🎀",
        "Ваш дзвінок — найкращий подарунок! 📱", "Приєднайтеся до щирих побажань! 🎶", "Згадайте, хто з близьких святкує! 👀",
        "Напишіть їм пару теплих рядків! 🔥", "Даруйте усмішки та квіти! 💐", "Щирі слова завжди доречні! 🌟",
        "Нехай друзі відчують вашу увагу! 💎", "Сьогодні день світла для цих імен! 🕯", "Гарна нагода відновити спілкування! 🤝",
        "Надішліть листівку або тепле слово! 📮", "Свято краще, коли про нього пам'ятають! 🎊", "Іменинники чекають на вашу увагу! 🍭",
        "Складіть коротке вітання для близьких! ✍️", "Хай ваше повідомлення зігріє когось! 🧣", "Теплі слова самі себе не напишуть! 😉",
        "Обійміть іменинників хоча б віртуально! 🤗", "Будьте першим, хто привітає сьогодні! 🥇", "Світ стає добрішим від вітань! 🌎"
    ]
    intros_advices = [
        "💡 <b>Корисний лайфхак:</b>", "🛠 <b>Спробуй це:</b>", "🎯 <b>Це спростить твоє життя:</b>", "🧩 <b>Маленька хитрість:</b>", "⚙️ <b>Оптимізуй свій день:</b>",
        "🛡 <b>Корисна порада:</b>", "🔑 <b>Секрет продуктивності:</b>", "🪁 <b>Легке рішення:</b>", "🔋 <b>Збережи енергію:</b>", "🧸 <b>Просто і геніально:</b>",
        "💡 <b>Тобі це допоможе:</b>", "📌 <b>Варто спробувати:</b>", "🛠 <b>Практична порада:</b>", "⏱ <b>Зеконом свій час:</b>", "💡 <b>Ідея для тебе:</b>",
        "🔧 <b>Розумний підхід:</b>", "🪄 <b>Магія побуту:</b>", "🧘 <b>Для твого комфорту:</b>", "⚡️ <b>Швидке вирішення:</b>", "🚀 <b>Лайфхак дня:</b>",
        "💡 <b>Візьми на озброєння:</b>", "📋 <b>Перевірений метод:</b>", "💡 <b>Цікавий трюк:</b>", "🎯 <b>Влучно і просто:</b>", "💡 <b>Як зробити краще:</b>",
        "🧰 <b>Твій інструмент:</b>", "💡 <b>Проста хитрість:</b>", "🤫 <b>Маленький секрет:</b>", "💡 <b>Геніально і просто:</b>", "💡 <b>Твоя перевага:</b>"
    ]
    intros_quotes = [
        "🌈 <b>Трохи мудрості:</b>", "💎 <b>Цінна думка:</b>", "📝 <b>Варто занотувати:</b>", "💭 <b>Думка дня:</b>", "🖋 <b>Слова зі змістом:</b>",
        "📖 <b>Мудрість віків:</b>", "🕊 <b>Для натхнення:</b>", "🌟 <b>Світла думка:</b>", "💡 <b>Філософія дня:</b>", "📜 <b>Цитата дня:</b>",
        "🗣 <b>Як сказав класик:</b>", "✍️ <b>Глибока думка:</b>", "⚖️ <b>Важливо пам'ятати:</b>", "🎭 <b>Слова, що надихають:</b>", "🧭 <b>Твій орієнтир:</b>",
        "🌅 <b>Думка для роздумів:</b>", "🎯 <b>Влучні слова:</b>", "🗝 <b>Ключ до розуміння:</b>", "🧩 <b>Збери думки:</b>", "☀️ <b>Теплі слова:</b>",
        "🕯 <b>Істина десь поруч:</b>", "📚 <b>Зі сторінок історії:</b>", "📌 <b>Запам'ятай це:</b>", "💡 <b>Світло розуму:</b>", "💎 <b>Словесний діамант:</b>",
        "🪴 <b>Зерно мудрості:</b>", "🌿 <b>Джерело натхнення:</b>", "🔭 <b>Погляд на життя:</b>", "🧭 <b>Життєвий компас:</b>", "🕊 <b>Слова, що гріють:</b>"
    ]
    intros_facts = [
        "🧠 <b>А чи знав ти, що:</b>", "🔍 <b>Цікавий факт:</b>", "🛰 <b>Погляд під іншим кутом:</b>", "📡 <b>Інформація для тебе:</b>", "⛲️ <b>Джерело знань:</b>",
        "🎬 <b>Факти, що вражають:</b>", "🌍 <b>Дивовижний світ:</b>", "💡 <b>Неймовірно, але факт:</b>", "🧐 <b>Хвилинка ерудиції:</b>", "📚 <b>Пізнавально:</b>",
        "🔬 <b>Науковий факт:</b>", "🔭 <b>Розширюємо кругозір:</b>", "🧠 <b>Їжа для розуму:</b>", "🤯 <b>Зрив мозку:</b>", "💡 <b>Чи відомо тобі:</b>",
        "🧩 <b>Цікавинка:</b>", "📖 <b>Сторінка фактів:</b>", "🌐 <b>З усього світу:</b>", "💡 <b>Несподіване відкриття:</b>", "🧭 <b>Цікаво знати:</b>",
        "💡 <b>Факт дня:</b>", "🗝 <b>Секрети світу:</b>", "📌 <b>Коротка довідка:</b>", "💡 <b>Оце так новина:</b>", "⚡️ <b>Вражаюче:</b>",
        "💡 <b>Захоплюючий факт:</b>", "🔬 <b>Трохи науки:</b>", "🧠 <b>Тренуй мозок:</b>", "💡 <b>Для роздумів:</b>", "🌍 <b>Світ навколо нас:</b>"
    ]

    book_captions = [
        "📖 Книги, які змусять вас забути про час. Зберігайте добірку!", "📚 Що почитати цього тижня? Тримайте кілька чудових ідей!",
        "🔖 Збережіть цей пост, щоб наступного разу не шукати, що почитати.", "☕️ Ідеальне чтиво для затишних вечорів з чашкою чаю.",
        "💡 Ці сторінки можуть змінити ваш погляд на звичні речі.", "📚 Добірка для тих, хто шукає натхнення та нові емоції.",
        "🧭 Книги, з якими можна вирушити в найцікавішу подорож.", "📖 Від цих книг просто неможливо відірватися!",
        "📌 Поповнюємо свій список 'must read'. Як вам такі варіанти?", "📚 Хороша книга — це завжди чудова ідея. Зберігайте!",
        "🧠 Література, яка змушує думати та аналізувати.", "📖 Час для себе — це час із книгою. Рекомендуємо!",
        "🔖 Добірка на випадок 'хочеться чогось цікавого, але не знаю чого'.", "📚 Кожна з цих книг варта того, щоб опинитися на вашій полиці.",
        "✨ Книги, що залишають післясмак і бажання читати ще.", "📖 Знайдіть свою наступну улюблену книгу серед цих варіантів.",
        "🛋 Закутатись у плед і читати — ось план на найближчі дні!", "📚 Шукаєте нову історію, в яку можна зануритись з головою? Тримайте!",
        "📌 Добірка, яку варто надіслати другу-книголюбу.", "📖 Відпочиньте від екранів — перегорніть паперові сторінки.",
        "📚 Книжкова рекомендація, яка точно не розчарує.", "🌟 Література, яка торкається найтонших струн душі.",
        "📖 Дозвольте цим книгам вкрасти ваш вільний час. Воно того варте!", "🔖 Якщо не знаєте, з чого почати читати, почніть із цієї добірки.",
        "📚 Інвестиція в себе — це час, проведений за хорошою книгою.", "🚀 Книги, які мотивують, надихають і захоплюють.",
        "📖 Для тих, хто цінує якісну літературу та глибокі сенси.", "📚 Ваш книжковий радар знайшов щось дуже цікаве. Зберігайте!",
        "☕️ Кава, тиша і одна з цих книг — рецепт ідеального вихідного.", "📌 Чудова компанія на декілька наступних вечорів забезпечена.",
        "📖 Ці автори точно знають, як утримати увагу читача.", "📚 Розширюємо горизонти: добірка, на яку варто звернути увагу.",
        "🔖 Зберігайте скріншот, щоб показати консультанту в книгарні!", "📖 Добірка для справжніх гурманів слова.",
        "🌟 Історії, які залишаться у вашій пам'яті надовго.", "📚 Шукаєте подарунок? Ці книги — безпрограшний варіант.",
        "📖 Не відкладайте хороше чтиво на потім. Обирайте свою книгу вже зараз!", "📌 Література, після якої хочеться помовчати і подумати.",
        "📚 Відкрийте для себе нові світи на сторінках цих книг.", "📖 Коли реальність втомлює, на допомогу приходять хороші книги.",
        "🔖 Ваша електронна бібліотека вимагає поповнення!", "📚 Свіжа порція книжкових рекомендацій спеціально для вас.",
        "📖 Читання — це телепатія. Послухайте, що хочуть сказати ці автори.", "🌟 Добірка, яка збере безліч збережень. Не пропустіть!",
        "📚 Книги, про які хочеться говорити і які хочеться обговорювати.", "📖 Приділіть 20 хвилин на день читанню, і ці книги змінять вас.",
        "📌 Знайти 'свою' книгу — це щастя. Можливо, вона саме тут.", "📚 Добірка, яка врятує від хандри.",
        "📖 Світ стає ширшим з кожною прочитаною сторінкою.", "📚 Заварюйте чай, обирайте книгу з добірки і насолоджуйтесь!"
    ]

    info_captions = [
        "📌 Збережіть себе, щоб не загубити!", "💡 Корисна шпаргалка на всі випадки життя.",
        "🛡 Важливо знати кожному. Перешліть близьким!", "🩺 Здоров'я та безпека понад усе. Зберігайте!",
        "🧩 Просто і зрозуміло про важливе.", "📌 Додайте в 'Збережене', колись обов'язково знадобиться.",
        "💡 Інструкція, яка має бути під рукою.", "🛑 Правила, які можуть врятувати здоров'я.",
        "📋 Коротка пам'ятка для вас та вашої родини.", "⚡️ Прості кроки для вирішення проблеми.",
        "🛡 Безпека починається зі знань. Читаємо!", "📌 Маленька, але дуже важлива інфографіка.",
        "💡 Знали про це? Збережіть, щоб пам'ятати!", "🚑 Корисна медична та побутова пам'ятка.",
        "🧩 Складна тема простими словами.", "📌 Шпаргалка, яку варто показати друзям.",
        "💡 Зберігайте на телефон, щоб завжди було під рукою.", "🛡 Ніхто не застрахований, тому краще знати!",
        "📋 Важливий чек-лист на сьогодні.", "⚡️ Дієві поради в зручному форматі.",
        "📌 Корисно знати: зберігаємо в закладки.", "💡 Лайфхак, який перевірено часом.",
        "🛑 Краще знати і не використати, ніж навпаки.", "📋 Ваш короткий гід по безпеці та здоров'ю.",
        "⚡️ Профілактика та перша допомога в одній картинці.", "📌 Нагадування, яке ніколи не буде зайвим.",
        "💡 Поділіться цим постом з тими, про кого піклуєтесь.", "🛡 Обізнаний — значит захищений!",
        "📋 Пам'ятка, яка економить нерви і час.", "⚡️ Максимум користі в одному зображенні.",
        "📌 Збережіть цю інструкцію прямо зараз.", "💡 Коротко, ясно і по суті.",
        "🛑 Базові знання для комфортного життя.", "📋 Ваш особистий довідник у форматі картинки.",
        "⚡️ Прості поради, які дають великий результат.", "📌 Не забувайте дбати про себе!",
        "💡 Зберігаємо і застосовуємо на практиці.", "🛡 Знання — це ваша броня.",
        "📋 Що робити, якщо... Коротка відповідь!", "⚡️ Інфографіка, яка розставляє все по поличках.",
        "📌 Корисний скріншот на ваш екран.", "💡 Пам'ятка для тих, хто цінує своє здоров'я.",
        "🛑 Правильні дії в потрібний момент.", "📋 Додайте в обране, щоб не шукати потім.",
        "⚡️ Важлива інформація, вміщена в один кадр."
    ]

    night_wishes = [
        "Тихого та затишного вечора! Час відпочити. 🌙", "Міцного сну та спокійної ночі! ✨",
        "Нехай вечір принесе лише релакс. 🍷", "Час відкласти справи і просто відпочити. 🛋"
    ]

    # --- ЛОГІКА ПУБЛІКАЦІЙ (РОЗКЛАД) ---

    if weekday == 2 and hour == 16:
        img = get_random_image("media/books")
        text = f"📚 <b>КНИЖКОВА ПОЛИЦЯ</b>\n\n{random.choice(book_captions)}"
        return text, img, None

    elif weekday == 3 and hour == 16:
        img = get_random_image("media/cinema")
        text = get_cinema_premieres()
        return text, img, None

    elif 5 <= hour < 11:
        img = get_random_image("media/morning")
        names = get_data_by_date('history')
        holidays = get_data_by_date('Holiday')
        history = get_data_by_date('Wiking')
        ny_days = (datetime.date(now.year + 1, 1, 1) - now.date()).days

        text = (
            f"🌅 <b>ДОБРОГО РАНКУ!</b>\n"
            f"📅 Сьогодні: <b>{now.strftime('%d.%m.%Y')}</b>\n"
            f"{divider}\n"
            f"🎂 <b>Іменини сьогодні святкують:</b>\n"
            f"└ {names}\n"
            f"<i>{random.choice(congrats)}</i>\n\n"
            f"🎉 <b>Свята:</b> {holidays}\n"
            f"📜 <b>Цей день в історії:</b> {history}\n"
            f"{divider}\n"
            f"{get_currency_logic()}\n"
            f"🎄 До Нового Року: {ny_days} дн.\n"
            f"{divider}\n"
            f"🔮 <b>ТВІЙ ПЕРСОНАЛЬНИЙ ГОРОСКОП ТА ПЕРЕДБАЧЕННЯ</b>\n"
            f"└ Дізнайся астрологічний прогноз і отримай своє особисте передбачення на день."
        )

        reply_markup = {
            "inline_keyboard": [
                [
                    {
                        "text": "✨ Дізнатися, що чекає сьогодні",
                        "url": MINI_APP_URL
                    }
                ]
            ]
        }
        return text, img, reply_markup

    elif 11 <= hour < 13:
        img = get_random_image("media/infographics")
        text = f"🗂 <b>Практикум життєвих ситуацій</b>\n\n{random.choice(info_captions)}"
        return text, img, None

    elif 13 <= hour < 16:
        img = None
        # Тепер беремо лише ОДНУ пораду замість 2-3
        advice = get_random_lines('lifehacks')

        text = f"🧩 <b>ПРОСТО ПРО СКЛАДНЕ:</b>\n\n{advice}\n\n<i>📌 Тисніть на кнопку нижче, щоб отримати пораду саме для вашої ситуації!</i>"

        # Додаємо клавіатуру з потрібним посиланням
        reply_markup = {
            "inline_keyboard": [
                [
                    {
                        "text": "💡 БІЛЬШЕ ПОРАД ТУТ",
                        "url": "https://t.me/lifechaksdaybot/lifechaks"
                    }
                ]
            ]
        }
        return text, img, reply_markup

    elif 17 <= hour < 20:
        img = get_random_image("media/parables")
        parable = get_random_lines('parables')
        text = f"📖 <b>КНИГА НА ВЕЧІР</b>\n\n{parable}\n\n<i>✨📖📚📕📗📘📙🔍📑📜🧠🎓✨ </i>"
        
        reply_markup = {
            "inline_keyboard": [
                [
                    {
                        "text": "📚 БІЛЬШЕ КНИГ",
                        "url": "https://t.me/boock1bot/boock"
                    }
                ]
            ]
        }
        return text, img, reply_markup

    elif hour >= 20 or hour < 5:
        img = get_random_image("media/evening")
        # 40 описів у перемішаному циклі: інший варіант кожного вечора.
        mini_app_variants = [
            ('🫧 А якщо клопоти сьогодні просто луснуть?', 'Напиши слово на кульці й торкнися її. А потім вирішуй: ще одна кулька, пригода зі змійкою чи тихий потяг? У Просторі є 75 способів провести маленьку паузу.', 'Лопнути перший клопіт ✨'),
            ('🐍 У цієї змійки незвичне меню', 'Вона збирає дрібні проблеми. Тобі лишається обрати напрямок і подивитися, скільки вона подужає. Спробуй один раунд — вечерю змійці вже подано.', 'Погодувати змійку клопотами'),
            ('🚪 За цими дверима вечір може піти інакше', 'Обери настрій, а Простір запропонує пригоду. Кумедну, затишну чи трохи загадкову — цікаво, які двері відкриються тобі сьогодні?', 'Відчинити двері пригоди'),
            ('🚃 Квиток є. Валізу збирати не треба', 'У тихому потязі можна обрати пейзаж і просто дивитися у вікно. Знайди свою нічну подорож — сьогодні цілком можна їхати без списку справ.', 'Зайняти місце біля вікна'),
            ('⚖️ Диван найняв адвоката', 'Справу «Диван проти ще одного завдання» вже слухають. Обирай репліки й дізнайся, чим закінчиться цей вечірній суд. Твоя версія фіналу чекає.', 'Зазирнути на засідання'),
            ('🐦 Голуби знову скликали нараду', 'Питання поважні. Учасники — теж, принаймні вони так вважають. Втруться у пташине засідання й перевір, куди приведуть твої рішення.', 'Дізнатися, що задумали голуби'),
            ('🌃 В одному з цих вікон є історія', 'Торкнися вікна нічного міста й відкрий маленьку сцену. Потім ще одного — якщо захочеться. Почни з того, яке першим приверне увагу.', 'Засвітити своє вікно'),
            ('🎚️ Як звучав би твій ідеальний вечір?', 'Дощ, сторінки, потяг чи тихі ноти? Змішай звуки на свій смак. Можливо, твоєму вечору бракувало саме такого маленького саундтреку.', 'Зібрати звук свого вечора'),
            ('💌 Завтрашньому тобі дещо передали', 'Поки що — чисту листівку. Додай свої слова, обери оформлення й збережи її. Напиши щось, що самому було б приємно прочитати завтра.', 'Створити листівку собі'),
            ('🏛️ У музеї звільнилося особливе місце', 'Для твоєї маленької перемоги. Навіть якщо сьогодні це «нарешті знайшовся другий носок». Обери подію, дай їй назву й зроби власний експонат.', 'Відкрити свою маленьку виставку'),
            ('🚀 У клопоту з’явився маршрут на Місяць', 'Напиши коротку записку й намалюй шлях ракети. Подивися, як вона вирушить у політ. Для цієї маленької космічної паузи скафандр не потрібен.', 'Підготувати ракету до старту'),
            ('🧺 День залишив плями? Є космічна пральня', 'Завантаж його дрібні пригоди й обери кумедний цикл. Цікаво, як виглядає прання дня в космосі? Відкрий майстерню та запусти свою версію.', 'Обрати цикл для цього дня'),
            ('🫖 Чайник має що сказати', 'Він бурчить, а ти ловиш ритм і відкриваєш клапан. Хто сьогодні краще відчуває момент — ти чи чайник із характером? Перевір у короткій грі.', 'Послухати цього буркотуна'),
            ('🎬 Якби твій день був фільмом…', 'Який жанр йому пасував би: комедія чи пригода? Обери події та фінальний кадр, а потім запусти трейлер. Режисерське крісло сьогодні твоє.', 'Змонтувати трейлер свого дня'),
            ('⏰ Будильник надто впевнений у завтрашньому ранку', 'Допоможи йому підготуватися — або хоча б вислухай його версію плану. У цій короткій історії ти обираєш відповіді. Якою буде кінцівка?', 'Дізнатися план будильника'),
            ('🍪 Печиво просить головну роль', 'Схоже, у театрі назріває маленька драма. Роздай ролі й допоможи герою вийти на сцену. Виріши, як розгорнеться ця дивна вистава.', 'Відкрити завісу'),
            ('🧊 За дверцятами холодильника хтось готує відповідь', 'Цього разу можна просто зазирнути заради розмови. Торкнися дверцят і познайомся з холодильником, якому точно є що додати до твого вечора.', 'Зазирнути: що він скаже?'),
            ('🛋️ До дивана веде лабіринт', 'Затишок уже десь поруч, але доріжка встигла заплутатися. Обери темп і знайди вихід. Цікаво, з якого повороту почнеться твій шлях?', 'Знайти дорогу до затишку'),
            ('🏰 Подушки готові до великого будівництва', 'Спробуй скласти з них фортецю й утримати рівновагу. Висота залежить від твоїх влучних моментів. Будівельний майданчик м’який — можна починати.', 'Покласти першу подушку'),
            ('🎣 Що сьогодні потрапить на гачок?', 'На цій риболовлі ловлять хороші моменти. Стеж за поплавцем і спробуй вчасно підсікти. Перший улов може стати приводом згадати щось приємне зі свого дня.', 'Закинути вудку'),
            ('🐈 Кіт знайшов гору відкритих вкладок', 'І, звісно, вирішив по них пострибати. Допоможи йому впоратися із зайвими вкладками. Цікаво, наскільки спритною буде ваша команда сьогодні?', 'Приєднатися до котячої операції'),
            ('☕ Чашці потрібен власний міст', 'Побудуй шлях через стіл і допоможи їй дістатися іншого боку. Подивися уважно: який маршрут спрацює? Спробуй свою інженерну ідею.', 'Прокласти шлях для чашки'),
            ('🌌 У небі ще немає твого сузір’я', 'З’єднай зорі послідовно й придумай назву. Можна урочисту, а можна таку, щоб самому стало смішно. Почни з першої точки.', 'Створити власне сузір’я'),
            ('🎼 Нічні музиканти чекають диригента', 'Послухай коротку послідовність і спробуй повторити ритм. Обери зручний темп — подивимося, як звучатиме ваш маленький вечірній виступ.', 'Спробувати перший ритм'),
            ('☁️ На що схожа хмара, якої ще немає?', 'Намалюй її — тоді й з’ясуємо. На кота, острів чи щось, чому ще треба придумати назву? Дай уяві кілька вільних хвилин.', 'Намалювати свою хмару'),
            ('🪴 Тут можна виростити маленьку паузу', 'Полий сад, додай світла й подивися, як він змінюється. Сьогодні вистачить однієї спокійної сцени. Обери, з чого почнеться твій затишний куточок.', 'Зазирнути у свій сад'),
            ('🔦 У темряві сховалися зорі', 'Проведи ліхтариком по небу й спробуй їх знайти. Яка спалахне першою? Почни свою маленьку пошукову експедицію — не поспішаючи.', 'Увімкнути зоряний ліхтарик'),
            ('🐠 Акваріум, у якому все можна розставити по-своєму', 'Додай рибок і камінці, а потім поспостерігай за їхнім тихим світом. Який куточок вийде саме в тебе? Відкрий сцену й почни з однієї деталі.', 'Створити свій підводний куточок'),
            ('🪨 З кількох камінців може початися цілий візерунок', 'Перекладай їх на березі, пробуй різні поєднання й залиш те, яке подобається. Тут немає правильної картинки — цікаво побачити твою.', 'Скласти візерунок на березі'),
            ('🍃 А що, як вітер слухатиметься твого пальця?', 'Проведи по екрану й задай напрямок листю та паперовим літачкам. Один рух — і сцена змінюється. Спробуй влаштувати власну маленьку повітряну прогулянку.', 'Намалювати напрямок вітру'),
            ('🏮 У нічному небі бракує одного ліхтарика', 'Обери для нього колір і відпусти вгору. Подивися на політ — а далі вирішуй, додати ще один чи залишити цю мить тихою.', 'Запалити свій ліхтарик'),
            ('📚 На цій полиці книжки трохи дивні', 'Усередині — короткі авторські історії, які можна прочитати за маленьку паузу. Обери назву навмання: цікаво, хто сьогодні стане героєм твого вечора?', 'Відкрити незвичайну книжку'),
            ('🪟 За запітнілим вікном є напис', 'Проведи пальцем, щоб його побачити. Можна відкривати по шматочку й здогадуватися, що там далі. Зазирни за першу прозору смужку.', 'Подивитися, що приховує вікно'),
            ('🪐 Космос підготував маленьку несподіванку', 'Обери небесний об’єкт і відкрий коротку цікавинку з джерелом. Можливо, знайдеш факт, який захочеться переказати комусь завтра. Почни свою екскурсію.', 'Зазирнути до планетарію'),
            ('🕵️ Звучить переконливо. А чи правда?', 'Обери версію у короткій вікторині, а потім відкрий пояснення й джерело. Тут цікаво навіть помилятися: можна дізнатися те, чого зовсім не очікував.', 'Перевірити першу здогадку'),
            ('🔎 У кімнаті заховалася підказка', 'Досліди вигадану сцену й виріши, яку одну річ варто змінити. Для цього детектива важлива уважність. Спробуй помітити деталь, із якої все почнеться.', 'Розпочати маленьке розслідування'),
            ('💡 Три деталі. Один дуже несподіваний винахід', 'Поєднай звичайні речі та подивися, яка машина з них вийде. А потім порівняй її з простішим рішенням. Уява вже може братися до роботи.', 'Зібрати свій дивний винахід'),
            ('📺 Прогноз вечора склали… предмети', 'Обери три деталі й отримай суто комедійний прогноз. Жодної серйозної аналітики — лише привід побачити знайомі речі з кумедного боку.', 'Подивитися свій прогноз вечора'),
            ('✂️ Поміняй кадри — і історія заграє інакше', 'У маленькій комедії порядок вирішує багато. Перестав сцени й подивися, що зміниться. Яку версію ти залишиш у своєму вечірньому монтажі?', 'Спробувати інший поворот історії'),
            ('✨ Не знаєш, чого хочеться? Почни з цікавості', 'У Просторі 75 маленьких пригод: від кульок і змійки до смішних історій та нічних пейзажів. Обери те, що зачепить погляд, і подаруй собі коротку паузу.', 'Знайти пригоду для цього вечора'),
        ]
        # До 05:00 триває попередній вечір. Дата вже у часовому поясі бота.
        evening_date = (now - datetime.timedelta(hours=5)).date()
        variant_order = list(range(len(mini_app_variants)))
        # Сталий seed зберігає порядок після перезапуску, зокрема у GitHub Actions.
        random.Random("prostir-evening-miniapp-v1").shuffle(variant_order)
        variant_index = variant_order[evening_date.toordinal() % len(variant_order)]
        mini_title, mini_description, mini_link_text = mini_app_variants[variant_index]
        text = (
            f"<b>{mini_title}</b>\n\n"
            f"{mini_description}\n\n"
            f'👉 <a href="https://t.me/pkksuperappbot/superapp"><b>{mini_link_text}</b></a>\n\n'
            f"{get_movie()}\n\n"
            f"✨ <i>{random.choice(night_wishes)}</i>"
        )
        return text, img, None

    else:
        img = get_random_image("media/day")
        text = f"{random.choice(intros_advices)}\n└ {get_random_lines('advices')}"
        return text, img, None

if __name__ == "__main__":
    content, photo, reply_markup = make_post()

    # Відправляємо в Telegram
    send_telegram(content, photo, reply_markup)

    # Відправляємо у Viber
    send_viber(content, photo)
