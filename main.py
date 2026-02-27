import requests
import random
import datetime
import os

# --- КЛЮЧІ ТА НАЛАШТУВАННЯ (З ВАШИХ СКРІНШОТІВ) ---
TMDB_API_KEY = "583e99233cb332aaf8ab0ded7a92dde7"
HOLIDAY_API_KEY = "17904126938947f694726e6423985558"

# ТУТ МАЮТЬ БУТИ ВАШІ ДАНІ (ПЕРЕВІРТЕ ЇХ ЩЕ РАЗ)
TELEGRAM_TOKEN = "ВСТАВТЕ_ВАШ_ТОКЕН_ТУТ"
TELEGRAM_CHAT_ID = "ВСТАВТЕ_ВАШ_CHAT_ID_ТУТ"

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML"  # HTML надійніший за Markdown для початківців
    }
    try:
        r = requests.post(url, json=payload, timeout=15)
        print(f"Статус відправки в Telegram: {r.status_code}")
        if r.status_code != 200:
            print(f"Помилка від Telegram: {r.text}")
        return r.json()
    except Exception as e:
        print(f"Критична помилка мережі: {e}")
        return None

def get_divider():
    divs = ["\n<b>━━━━━━━━━━━━━━</b>\n", "\n✨ <b>• • • • • •</b> ✨\n", "\n<b>────────────────</b>\n"]
    return random.choice(divs)

def get_full_currency():
    res = "💰 <b>КУРС ВАЛЮТ</b>\n"
    try:
        p = requests.get("https://api.privatbank.ua/p24api/pubinfo?exchange&json&coursid=11", timeout=10).json()
        usd = next(i for i in p if i['ccy'] == 'USD')
        eur = next(i for i in p if i['ccy'] == 'EUR')
        res += f"🏦 Приват: 🇺🇸 {usd['buy'][:5]}/{usd['sale'][:5]} | 🇪🇺 {eur['buy'][:5]}/{eur['sale'][:5]}\n"
    except Exception as e:
        print(f"Помилка валюти Приват: {e}")
        res += "🏦 Приват: Оновлюється...\n"
    return res

def get_holidays():
    now = datetime.datetime.now()
    url = f"https://holidays.abstractapi.com/v1/?api_key={HOLIDAY_API_KEY}&country=UA&year={now.year}&month={now.month}&day={now.day}"
    try:
        r = requests.get(url, timeout=10).json()
        if r and isinstance(r, list):
            h_names = [h['name'] for h in r]
            return "🎊 <b>СВЯТА:</b> " + ", ".join(h_names)
        return "🎊 <b>СВЯТА:</b> Офіційних свят немає"
    except Exception as e:
        print(f"Помилка свят: {e}")
        return "🎊 <b>СВЯТА:</b> Інформація оновлюється"

def get_movie():
    try:
        page = random.randint(1, 10)
        url = f"https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}&language=uk-UA&page={page}"
        r = requests.get(url, timeout=10).json()
        m = random.choice(r['results'])
        title = m.get('title', 'Цікавий фільм')
        rating = m.get('vote_average', '7.0')
        overview = m.get('overview', 'Опис скоро буде...')
        return f"🎬 <b>ВЕЧІРНІЙ КІНОЗАЛ</b>\n🎥 <b>{title}</b>\n⭐ Рейтинг: {rating}\n🍿 {overview[:200]}..."
    except Exception as e:
        print(f"Помилка кіно: {e}")
        return "🎬 Подивіться сьогодні щось із класики!"

def get_line(file):
    try:
        if not os.path.exists(file):
            print(f"Увага: Файл {file} не знайдено!")
            return "Дані оновлюються"
        with open(file, 'r', encoding='utf-8') as f:
            lines = [l.strip() for l in f.readlines() if l.strip()]
            return random.choice(lines) if lines else "Дані відсутні"
    except Exception as e:
        print(f"Помилка читання файлу {file}: {e}")
        return "Дані недоступні"

def make_post():
    # Розрахунок часу (Київ)
    hour = (datetime.datetime.now().hour + 2) % 24 
    
    if 5 <= hour < 11:
        today = datetime.date.today()
        ny = datetime.date(today.year + 1, 1, 1)
        return (f"🌅 <b>ДОБРОГО РАНКУ!</b>\n📅 {today.strftime('%d.%m.%Y')}\n{get_divider()}"
                f"🎂 Іменини: {get_line('names.txt')}\n{get_holidays()}\n📜 Історія: {get_line('history.txt')}\n"
                f"{get_divider()}{get_full_currency()}\n🎄 До НР: {(ny-today).days} дн.\n"
                f"{get_divider()}💡 Лайфхак: {get_line('advices.txt')}")
    
    elif 11 <= hour < 18:
        return f"🌤 <b>ДЕННИЙ ВИПУСК</b>\n\n💡 Лайфхак: {get_line('advices.txt')}\n{get_divider()}🧐 Факт: {get_line('facts.txt')}"
    
    else:
        return (f"🌙 <b>ВЕЧІРНІЙ ПОСТ</b>\n\n💡 Лайфхак: {get_line('advices.txt')}\n{get_divider()}"
                f"🧐 Факт: {get_line('facts.txt')}\n{get_divider()}😂 Жарт: {get_line('jokes.txt')}\n"
                f"{get_divider()}\n{get_movie()}")

if __name__ == "__main__":
    content = make_post()
    send_telegram(content)
