import requests
import random
import datetime
import os
import pytz

# --- НАЛАШТУВАННЯ ---
TMDB_API_KEY = os.environ.get("TMDB_API_KEY", "583e99233cb332aaf8ab0ded7a92dde7")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "8779933996:AAFtTmrPZ3qME5WV3ZRf7rfOHKzxbCsmSFY")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "653398188")
KIEV_TZ = pytz.timezone('Europe/Kiev')

def get_now():
    return datetime.datetime.now(KIEV_TZ)

def send_telegram(text, photo_path=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/send{'Photo' if photo_path else 'Message'}"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "caption" if photo_path else "text": text, "parse_mode": "HTML"}
    
    # Відключаємо прев'ю посилань для чистішого вигляду тексту
    if not photo_path:
        payload["disable_web_page_preview"] = True

    if photo_path and os.path.exists(photo_path):
        with open(photo_path, 'rb') as photo:
            return requests.post(url, data=payload, files={"photo": photo}).json()
    return requests.post(url, json=payload).json()

def get_detailed_info(movie_id):
    """Отримує жанри та акторів для конкретного фільму"""
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=uk-UA&append_to_response=credits"
        data = requests.get(url, timeout=10).json()
        genres = [g['name'] for g in data.get('genres', [])]
        genres_str = ", ".join(genres) if genres else "Кіно"
        cast = [person['name'] for person in data.get('credits', {}).get('cast', [])[:3]]
        cast_str = ", ".join(cast) if cast else "Інформація відсутня"
        return genres_str, cast_str
    except:
        return "Кіно", "Інформація відсутня"

def get_cinema_premieres():
    """Збирає 10 фільмів з деталями"""
    try:
        url = f"https://api.themoviedb.org/3/movie/now_playing?api_key={TMDB_API_KEY}&language=uk-UA&region=UA"
        r = requests.get(url, timeout=10).json()
        movies = r.get('results', [])[:10]
        
        if not movies: return "🎬 Нових прем'єр поки немає."
        
        res = "🎞 <b>ЗАРАЗ У КІНОТЕАТРАХ УКРАЇНИ:</b>\n\n"
        for m in movies:
            title = m.get('title', 'Без назви')
            movie_id = m.get('id')
            genres, cast = get_detailed_info(movie_id)
            res += f"🎬 <b>{title.upper()}</b>\n"
            res += f"🎭 <i>{genres}</i>\n"
            res += f"👥 <i>{cast}</i>\n\n"
        return res
    except:
        return "🎬 Час обрати фільм для вечора!"

def get_currency_logic():
    res = "💰 <b>КУРС ВАЛЮТ</b>\n"
    try:
        p = requests.get("https://api.privatbank.ua/p24api/pubinfo?exchange&json&coursid=11", timeout=5).json()
        usd_p = next(i for i in p if i['ccy'] == 'USD')
        eur_p = next(i for i in p if i['ccy'] == 'EUR')
        m = requests.get("https://api.monobank.ua/bank/currency", timeout=5).json()
        usd_m = next(i for i in m if i['currencyCodeA'] == 840 and i['currencyCodeB'] == 980)
        eur_m = next(i for i in m if i['currencyCodeA'] == 978 and i['currencyCodeB'] == 980)
        res += f"🏦 <b>ПриватБанк:</b>\n└ USD: {usd_p['buy'][:5]} / {usd_p['sale'][:5]} | EUR: {eur_p['buy'][:5]} / {eur_p['sale'][:5]}\n"
        res += f"🐾 <b>Монобанк:</b>\n└ USD: {usd_m['rateBuy']:.2f} / {usd_m['rateSell']:.2f} | EUR: {eur_m['rateBuy']:.2f} / {eur_m['rateSell']:.2f}"
    except: res += "⚠️ Курс тимчасово недоступний"
    return res

def get_data_by_date(filename):
    """Шукає дані за форматом MM-DD (наприклад 01-01)"""
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

    final_wishes = [
        "✨ Приємного перегляду!", "🍿 Не забудьте про попкорн!", "🎬 До зустрічі у кінозалі!", 
        "📽 Гарного вечора за переглядом!", "🌟 Нехай фільм перевершить очікування!", 
        "🎫 Квитки вже чекають на вас!", "🎭 Емоційного перегляду!", "🥤 Велика кола сама себе не вип'є!", 
        "🧐 Обирайте серцем, дивіться очима!", "🌈 Магії великого екрана вам!", 
        "🎞 Життя — це кіно, обирайте найкраще!", "🤫 Тиші у залі та яскравих вражень!", 
        "🛋 Влаштовуйтеся зручніше!", "👀 Побачимось на прем'єрі!", "🕯 Атмосферного вам вечора!", 
        "🤘 Нехай фільм буде драйвовим!", "🧠 Їжі для роздумів після сеансу!", 
        "💙 Підтримуйте українські кінотеатри!", "💛 До зустрічі на головному екрані міста!", 
        "🤩 Нехай цей фільм стане вашим улюбленим!", "🥳 Веселого перегляду всією компанією!", 
        "💘 Ідеальний план для побачення!", "🔥 Буде гаряче, не пропустіть!", 
        "🌑 Час зануритися у темряву кінозалу!", "⚡️ Заряджайтеся енергією кіно!", 
        "🤖 Навіть роботи люблять хороші фільми!", "🦄 Казкових емоцій від перегляду!", 
        "🧩 Зберіть свій пазл вражень!", "🛶 Вперед назустріч пригодам!", 
        "💎 Знайдіть свій кінодіамант!", "📣 Поділіться потім враженнями!", 
        "🕰 Час для кіно завжди вчасно!", "👒 Дивіться красиво!", "👟 Взувайтеся і біжіть у кіно!", 
        "🌌 Нескінченних вам кіновсесвітів!", "🥇 Тільки найкращих прем'єр!", 
        "🎁 Кіно — це завжди подарунок для душі!", "🪁 Легкого перегляду!", 
        "🧸 Навіть дітям буде цікаво!", "🛸 Космічного задоволення від картинки!", 
        "🛡 Будьте героями власного життя!", "🗝 Відкрийте для себе нову історію!", 
        "🪁 Нехай фантазія не має меж!", "⚖️ Оберіть свій ідеальний жанр!", 
        "🧱 Будуйте плани на вихідні навколо кіно!", "🌋 Вибухових емоцій!", 
        "❄️ Зігрівайтеся атмосферою кінозалу!", "🍃 Свіжих вражень від новинок!", 
        "🐾 Слідуйте за цікавим сюжетом!", "🦾 Міцного здоров'я та гарного кіно!"
    ]

    # --- ЛОГІКА ЧЕТВЕРГА (КІНОАФІША 16:00) ---
    if weekday == 3 and hour == 16:
        cinema_divider = "🎬✨🎬✨🎬✨🎬✨🎬"
        bottom_divider = "⭐️🍿⭐️🍿⭐️🍿⭐️🍿⭐️"
        cinema_block = get_cinema_premieres()
        wish = random.choice(final_wishes)
        
        text = (f"🗓 <b>КІНОАФІША • {now.strftime('%d.%m.%Y')}</b>\n"
                f"{cinema_divider}\n\n"
                f"{cinema_block}"
                f"{bottom_divider}\n"
                f"✨ {wish}")
        return text, None  # Повертаємо None для фото, щоб не було картинки на вечір

    # 🌅 РАНОК (5:00 - 10:59)
    if 5 <= hour < 11:
        img = get_random_image("media/morning")
        names = get_data_by_date('history')
        holidays = get_data_by_date('Holiday')
        history = get_data_by_date('Wiking')
        ny_days = (datetime.date(now.year + 1, 1, 1) - now.date()).days
        chosen_file = random.choice(['advices', 'facts', 'jokes'])
        random_info = get_random_lines(chosen_file)

        if chosen_file == 'advices':
            intro = random.choice(intros_advices)
        elif chosen_file == 'facts':
            intro = random.choice(intros_facts)
        else:
            intro = random.choice(intros_quotes)

        text = (f"🌅 <b>ДОБРОГО РАНКУ!</b>\n"
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
                f"{intro}\n"
                f"└ {random_info}")
        return text, img

    # 🌙 ВЕЧІР (Після 20:00)
    elif hour >= 20 or hour < 5:
        img = get_random_image("media/evening")
        a = get_random_lines('advices')
        f = get_random_lines('facts')
        j = get_random_lines('jokes')
        text = (f"{random.choice(intros_advices)}\n└ {a}\n\n"
                f"{random.choice(intros_facts)}\n└ {f}\n\n"
                f"😂 <b>Гумор:</b>\n└ {j}\n\n"
                f"{get_movie()}")
        return text, img

    # 🌤 ДЕНЬ (Інші пости 11:00, 13:30, 17:00)
    else:
        img = get_random_image("media/evening")
        text = (f"{random.choice(intros_advices)}\n└ {get_random_lines('advices')}\n\n"
                f"{random.choice(intros_facts)}\n└ {get_random_lines('facts')}")
        return text, img

if __name__ == "__main__":
    content, photo = make_post()
    send_telegram(content, photo)
