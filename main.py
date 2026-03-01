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
    if photo_path and os.path.exists(photo_path):
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
        with open(photo_path, 'rb') as photo:
            payload = {"chat_id": TELEGRAM_CHAT_ID, "caption": text, "parse_mode": "HTML"}
            files = {"photo": photo}
            r = requests.post(url, data=payload, files=files)
    else:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"}
        r = requests.post(url, json=payload)
    return r.json()

def get_currency_logic():
    res = "💰 <b>КУРС ВАЛЮТ</b>\n"
    try:
        # ПриватБанк
        p = requests.get("https://api.privatbank.ua/p24api/pubinfo?exchange&json&coursid=11", timeout=10).json()
        usd_p = next(i for i in p if i['ccy'] == 'USD')
        eur_p = next(i for i in p if i['ccy'] == 'EUR')
        
        # Монобанк
        m = requests.get("https://api.monobank.ua/bank/currency", timeout=10).json()
        usd_m = next(i for i in m if i['currencyCodeA'] == 840 and i['currencyCodeB'] == 980)
        eur_m = next(i for i in m if i['currencyCodeA'] == 978 and i['currencyCodeB'] == 980)
        
        res += f"🏦 <b>ПриватБанк:</b>\n└ USD: {usd_p['buy'][:5]} / {usd_p['sale'][:5]} | EUR: {eur_p['buy'][:5]} / {eur_p['sale'][:5]}\n"
        res += f"🐾 <b>Монобанк:</b>\n└ USD: {usd_m['rateBuy']:.2f} / {usd_m['rateSell']:.2f} | EUR: {eur_m['rateBuy']:.2f} / {eur_m['rateSell']:.2f}"
    except Exception as e:
        res += "⚠️ Курс тимчасово недоступний"
    return res

def get_data_by_date(filename):
    """Шукає рядок, що починається з MM-DD (як на твоїх скріншотах)"""
    try:
        # Формат MM-DD (наприклад, 03-01), як у твоїх файлах Holiday та Wiking
        today_str = get_now().strftime("%m-%d") 
        if not os.path.exists(filename): return "Дані відсутні"
        
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip().startswith(today_str):
                    # Повертаємо все після дати (обрізаємо перші 5-6 символів)
                    content = line.strip()[5:].strip()
                    return content if content else "Дані оновлюються"
        return "Дані оновлюються"
    except Exception as e:
        return f"Помилка файлу"

def get_random_lines(filename, count=1):
    try:
        if not os.path.exists(filename): return ["Дані відсутні"]
        with open(filename, 'r', encoding='utf-8') as f:
            lines = [l.strip() for l in f.readlines() if l.strip()]
        if not lines: return ["Дані відсутні"]
        return random.sample(lines, min(len(lines), count))
    except: return ["Помилка зчитування"]

def days_to_ny():
    today = get_now().date()
    ny = datetime.date(today.year, 12, 31) + datetime.timedelta(days=1)
    if today >= datetime.date(today.year, 1, 1) and today < datetime.date(today.year, 1, 2):
        return 0
    return (ny - today).days

def make_post():
    now = get_now()
    
    # 30 варіантів заклику до привітання
    congratulation_calls = [
        "Не забудьте привітати знайомих! 🥂", "Чудова нагода зателефонувати близьким! 🎈",
        "Обов'язково надішліть їм тепле вітання! 🎁", "Маленьке SMS зробить їхній день кращим! 💌",
        "Поділіться радістю з іменинниками! ✨", "Привітання зігріває серце. Напишіть їм! 😊",
        "Сьогодні гарний день для добрих слів! ☀️", "Встигніть побажати всього найкращого! 🎂",
        "Ангели радіють, коли ви вітаєте друзів! 👼", "Ваше привітання сьогодні дуже чекають! 🧸",
        "Не тримайте добро в собі — привітайте! 🕊", "Зробіть приємний сюрприз іменинникам! 🎀",
        "Ваш дзвінок — найкращий подарунок! 📱", "Приєднайтеся до щирих вітань! 🎶",
        "Згадайте, хто з близьких сьогодні святкує! 👀", "Напишіть їм пару теплих рядків! 🔥",
        "Даруйте усмішки сьогодні! 💐", "Щирі слова завжди доречні! 🌟",
        "Нехай друзі відчують вашу увагу! 💎", "Сьогодні день світла для цих імен! 🕯",
        "Гарна нагода відновити спілкування! 🤝", "Надішліть листівку або тепле слово! 📮",
        "Свято краще, коли про нього пам'ятають! 🎊", "Іменинники чекають на вашу увагу! 🍭",
        "Складіть коротке вітання для близьких! ✍️", "Хай ваше повідомлення зігріє когось! 🧣",
        "Теплі слова самі себе не напишуть! 😉", "Обійміть іменинників хоча б віртуально! 🤗",
        "Будьте першим, хто привітає героїв дня! 🥇", "Світ стає добрішим від вітань! 🌎"
    ]

    advice_intros = ["💡 Порада:", "🛠 Лайфхак:", "🧠 Хитрість:", "✨ Пропозиція:", "📝 На замітку:"]

    # Збираємо дані
    names = get_data_by_date('history.txt') # Файл з іменами (іменини)
    holidays = get_data_by_date('Holiday.txt') # Свята
    history = get_data_by_date('Wiking.txt') # Цей день в історії
    advice = get_random_lines('advices.txt', 1)[0]
    
    text = (f"🌅 <b>ДОБРОГО РАНКУ!</b>\n"
            f"📅 Сьогодні: {now.strftime('%d.%m.%Y')}\n"
            f"━━━━━━━━━━━━━━\n"
            f"🎂 <b>Іменини сьогодні святкують:</b>\n"
            f"└ 👤 {names}\n"
            f"<i>{random.choice(congratulation_calls)}</i>\n\n"
            f"🎉 <b>Свята:</b> {holidays}\n"
            f"📜 <b>Цей день в історії:</b> {history}\n"
            f"━━━━━━━━━━━━━━\n"
            f"{get_currency_logic()}\n"
            f"🎄 До Нового Року: {days_to_ny()} дн.\n"
            f"━━━━━━━━━━━━━━\n"
            f"{random.choice(advice_intros)}\n"
            f"└ {advice}")
            
    return text

if __name__ == "__main__":
    content = make_post()
    # Спробуємо знайти рандомне фото для ранку
    files = [f for f in os.listdir("media/morning") if f.lower().endswith(('.png', '.jpg', '.jpeg'))] if os.path.exists("media/morning") else []
    photo = os.path.join("media/morning", random.choice(files)) if files else None
    
    send_telegram(content, photo)
