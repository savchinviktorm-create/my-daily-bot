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
    if photo_path and os.path.exists(photo_path):
        with open(photo_path, 'rb') as photo:
            return requests.post(url, data=payload, files={"photo": photo}).json()
    return requests.post(url, json=payload).json()

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

# Функція для витягування кількох рандомних рядків (для лайфхаків о 13:00)
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
        "🎬 <b>Афіша тижня:</b>", "🍿 <b>Кіноновинки в Україні:</b>", "🎟 <b>Заплануй похід у кіно:</b>"
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

    congrats = [
        "Не забудьте привітати знайомих! 🥂", "Чудова нагода зателефонувати друзям! 🎈", "Надішліть їм тепле вітання! 🎁",
        "Маленьке SMS зробить їхній день кращим! 💌", "Поділіться радістю з іменинниками! ✨", "Привітання зігріває серце. Напишіть їм! 😊"
    ]

    intros_advices = ["💡 <b>Корисний лайфхак:</b>", "🛠 <b>Спробуй це:</b>", "🎯 <b>Це спростить твоє життя:</b>"]
    intros_facts = ["🧠 <b>А чи знав ти, що:</b>", "🔍 <b>Цікавий факт:</b>", "🔬 <b>Науковий факт:</b>"]
    intros_quotes = ["🌈 <b>Трохи мудрості:</b>", "💎 <b>Цінна думка:</b>", "💭 <b>Думка дня:</b>"]
    
    # 50 описів для блоку з книгами (Середа 16:00)
    book_captions = [
        "📖 Книги, які змусять вас забути про час. Зберігайте добірку!", "📚 Що почитати цього тижня? Тримайте кілька ідей!",
        "🔖 Збережіть цей пост, щоб не шукати, що почитати.", "☕️ Ідеальне чтиво для затишних вечорів.",
        "💡 Ці сторінки змінять ваш погляд на звичні речі.", "📚 Добірка для тих, хто шукає натхнення.",
        "🧭 Вирушайте в подорож, не виходячи з дому.", "📖 Від цих книг неможливо відірватися!",
        "📌 Поповнюємо свій список 'must read'.", "📚 Хороша книга — це завжди чудова ідея.",
        "🧠 Література, яка змушує думати.", "📖 Час для себе — це час із книгою.",
        "🔖 Коли хочеться чогось цікавого, але не знаєш чого.", "📚 Кожна з цих книг варта вашої полиці.",
        "✨ Книги, що залишають післясмак.", "📖 Знайдіть свою наступну улюблену історію.",
        "🛋 Закутатись у плед і читати — ідеальний план!", "📚 Шукаєте нову історію? Тримайте!",
        "📌 Добірка, яку варто надіслати другу.", "📖 Відпочиньте від екранів — перегорніть сторінки.",
        "📚 Книжкова рекомендація, яка не розчарує.", "🌟 Література, яка торкається душі.",
        "📖 Дозвольте цим книгам вкрасти ваш час.", "🔖 Якщо не знаєте, з чого почати, почніть звідси.",
        "📚 Інвестиція в себе — це час за книгою.", "🚀 Книги, які мотивують і надихають.",
        "📖 Для тих, хто цінує якісну літературу.", "📚 Ваш книжковий радар знайшов скарб.",
        "☕️ Кава, тиша і книга — рецепт ідеального вечора.", "📌 Чудова компанія на вихідні.",
        "📖 Ці автори знають, як утримати увагу.", "📚 Розширюємо горизонти.",
        "🔖 Покажіть цей пост консультанту в книгарні!", "📖 Добірка для гурманів слова.",
        "🌟 Історії, які залишаться у пам'яті надовго.", "📚 Шукаєте подарунок? Це безпрограшний варіант.",
        "📖 Не відкладайте читання на потім.", "📌 Література, після якої хочеться подумати.",
        "📚 Відкрийте для себе нові світи.", "📖 Коли реальність втомлює, рятують книги.",
        "🔖 Ваша бібліотека вимагає поповнення!", "📚 Свіжа порція книжкових рекомендацій.",
        "📖 Читання — це телепатія крізь час.", "🌟 Добірка, яка заслуговує на збереження.",
        "📚 Книги, про які хочеться говорити.", "📖 20 хвилин читання на день змінюють усе.",
        "📌 Знайти 'свою' книгу — це щастя.", "📚 Добірка, яка врятує від хандри.",
        "📖 Світ ширшає з кожною сторінкою.", "📚 Заварюйте чай і насолоджуйтесь!"
    ]

    # 45 заготовок для інфографіки (11:00)
    info_captions = [
        "📌 Збережіть собі, щоб не загубити!", "💡 Корисна шпаргалка на всі випадки життя.",
        "🛡 Важливо знати кожному. Перешліть близьким!", "🩺 Здоров'я та безпека понад усе. Зберігайте!",
        "🧩 Просто і зрозуміло про важливе.", "📌 Додайте в 'Збережене', обов'язково знадобиться.",
        "💡 Інструкція, яка має бути під рукою.", "🛑 Правила, які можуть врятувати здоров'я.",
        "📋 Коротка пам'ятка для вас.", "⚡️ Прості кроки для вирішення проблеми.",
        "🛡 Безпека починається зі знань.", "📌 Маленька, але дуже важлива інфографіка.",
        "💡 Знали про це? Збережіть!", "🚑 Корисна медична та побутова пам'ятка.",
        "🧩 Складна тема простими словами.", "📌 Шпаргалка, яку варто показати друзям.",
        "💡 Зберігайте на телефон.", "🛡 Ніхто не застрахований, тому краще знати!",
        "📋 Важливий чек-лист на сьогодні.", "⚡️ Дієві поради в зручному форматі.",
        "📌 Корисно знати: зберігаємо.", "💡 Лайфхак, який перевірено часом.",
        "🛑 Краще знати і не використати.", "📋 Ваш гід по безпеці.",
        "⚡️ Перша допомога в одній картинці.", "📌 Нагадування, яке не буде зайвим.",
        "💡 Поділіться цим постом.", "🛡 Обізнаний — значить захищений!",
        "📋 Пам'ятка, яка економить час.", "⚡️ Максимум користі в одному зображенні.",
        "📌 Збережіть цю інструкцію прямо зараз.", "💡 Коротко, ясно і по суті.",
        "🛑 Базові знання для комфортного життя.", "📋 Довідник у форматі картинки.",
        "⚡️ Прості поради, великий результат.", "📌 Не забувайте дбати про себе!",
        "💡 Зберігаємо і застосовуємо.", "🛡 Знання — це ваша броня.",
        "📋 Що робити, якщо... Коротка відповідь!", "⚡️ Інфографіка, яка розставляє все по поличках.",
        "📌 Корисний скріншот.", "💡 Пам'ятка для тих, хто цінує здоров'я.",
        "🛑 Правильні дії в потрібний момент.", "📋 Додайте в обране.", "⚡️ Важлива інформація в одному кадрі."
    ]

    night_wishes = [
        "Тихого та затишного вечора! Час відпочити. 🌙", "Солодких снів та спокійної ночі! ✨", 
        "Нехай вечір принесе лише релакс. 🍷", "Час відкласти справи і просто відпочити. 🛋"
    ]

    # СЕРЕДА 16:00 - КНИЖКОВІ ДОБІРКИ
    if weekday == 2 and hour == 16:
        img = get_random_image("media/books")
        text = f"📚 <b>КНИЖКОВА ПОЛИЦЯ</b>\n\n{random.choice(book_captions)}"
        return text, img

    # ЧЕТВЕР 16:00 - КІНОПРЕМ'ЄРИ
    elif weekday == 3 and hour == 16:
        img = get_random_image("media/evening")
        text = get_cinema_premieres()
        return text, img

    # 🌅 РАНОК (5:00 - 10:59) - Основний блок
    elif 5 <= hour < 11:
        img = get_random_image("media/morning")
        names = get_data_by_date('history')
        holidays = get_data_by_date('Holiday')
        history = get_data_by_date('Wiking')
        ny_days = (datetime.date(now.year + 1, 1, 1) - now.date()).days
        
        # Вибираємо факт тільки тут
        chosen_file = random.choice(['advices', 'facts', 'jokes'])
        random_info = get_random_lines(chosen_file)

        if chosen_file == 'advices': intro = random.choice(intros_advices)
        elif chosen_file == 'facts': intro = random.choice(intros_facts)
        else: intro = random.choice(intros_quotes)

        text = (f"🌅 <b>ДОБРОГО РАНКУ!</b>\n"
                f"📅 Сьогодні: <b>{now.strftime('%d.%m.%Y')}</b>\n"
                f"{divider}\n"
                f"🎂 <b>Іменини сьогодні святкують:</b>\n└ {names}\n"
                f"<i>{random.choice(congrats)}</i>\n\n"
                f"🎉 <b>Свята:</b> {holidays}\n"
                f"📜 <b>Цей день в історії:</b> {history}\n"
                f"{divider}\n"
                f"{get_currency_logic()}\n"
                f"🎄 До Нового Року: {ny_days} дн.\n"
                f"{divider}\n"
                f"{intro}\n└ {random_info}")
        return text, img

    # ☀️ 11:00 - ІНФОГРАФІКА
    elif hour == 11:
        img = get_random_image("media/infographics")
        text = f"🗂 <b>КОРИСНА ПАМ'ЯТКА</b>\n\n{random.choice(info_captions)}"
        return text, img

    # 🕒 13:00 - 3-5 ЛАЙФХАКІВ + КАРТИНКА (Без фактів)
    elif hour == 13:
        img = get_random_image("media/lifehacks")
        count = random.randint(3, 5)
        advices = get_multiple_random_lines('advices', count)
        
        text = f"💡 <b>ТОП-{count} ЛАЙФХАКІВ:</b>\n\n"
        for i, advice in enumerate(advices, 1):
            text += f"<b>{i}.</b> {advice}\n\n"
        text += "<i>📌 Зберігайте, щоб спростити собі життя!</i>"
        return text, img

    # 🌆 17:00 - ПРИТЧА (Без фактів і лайфхаків)
    elif hour == 17:
        img = get_random_image("media/evening") # Або створи media/parables
        parable = get_random_lines('parables')
        text = f"📖 <b>ВЕЧІРНЯ ПРИТЧА</b>\n\n{parable}\n\n<i>✨ Задумайтесь про це...</i>"
        return text, img

    # 🌙 ВЕЧІР (Після 20:00) - Анекдот + Фільм + Побажання
    elif hour >= 20 or hour < 5:
        img = get_random_image("media/evening")
        j = get_random_lines('jokes')
        text = (f"😂 <b>Хвилинка гумору:</b>\n└ {j}\n\n"
                f"{get_movie()}\n\n"
                f"✨ <i>{random.choice(night_wishes)}</i>")
        return text, img

    # ЗАПАСНИЙ ВАРІАНТ
    else:
        img = get_random_image("media/day")
        text = (f"{random.choice(intros_advices)}\n└ {get_random_lines('advices')}")
        return text, img

if __name__ == "__main__":
    content, photo = make_post()
    send_telegram(content, photo)
