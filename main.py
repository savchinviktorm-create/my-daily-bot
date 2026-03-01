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
    target_file = filename if os.path.exists(filename) else f"{filename}.txt"
    if not os.path.exists(target_file): return "Дані відсутні"
    try:
        today_str = get_now().strftime("%m-%d")
        with open(target_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip().startswith(today_str):
                    return line.strip()[5:].lstrip(' —-–:.').strip()
        return "Сьогодні без особливих подій"
    except: return "Помилка читання"

def get_random_lines(filename):
    target_file = filename if os.path.exists(filename) else f"{filename}.txt"
    if not os.path.exists(target_file): return "Дані оновлюються"
    try:
        with open(target_file, 'r', encoding='utf-8') as f:
            lines = [l.strip() for l in f.readlines() if l.strip()]
        return random.choice(lines) if lines else "Дані оновлюються"
    except: return "Помилка файлу"

def make_post():
    now = get_now()
    divider = "✨ ✨ ✨ ✨ ✨"

    # 30 заготовок для Іменин
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

    # 30 заготовок для ПОРАД (advices)
    advices_intros = [
        "💡 <b>Тобі це допоможе:</b>", "🛠 <b>Спробуй цей лайфхак:</b>", "📝 <b>Варто занотувати:</b>", "🎯 <b>Це спростить твоє життя:</b>",
        "🧐 <b>Лови круту ідею:</b>", "📎 <b>На замітку:</b>", "🛡 <b>Корисна порада:</b>", "🔋 <b>Для твоєї продуктивності:</b>",
        "🔑 <b>Секрет успіху:</b>", "🧪 <b>Перевірений метод:</b>", "🧩 <b>Маленька хитрість:</b>", "🚀 <b>Для твого розвитку:</b>",
        "⚡️ <b>Швидка допомога:</b>", "🧘 <b>Для твого комфорту:</b>", "🧭 <b>Твій орієнтир:</b>", "🦾 <b>Зроби своє життя легшим:</b>",
        "✅
