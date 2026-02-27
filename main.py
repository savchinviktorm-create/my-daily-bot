import requests
import random
import datetime
import os

# КЛЮЧІ З ВАШИХ СКРІНШОТІВ
TMDB_API_KEY = "583e99233cb332aaf8ab0ded7a92dde7"
HOLIDAY_API_KEY = "17904126938947f694726e6423985558"

def get_divider():
    dividers = ["\n━━━━━━━━━━━━━━\n", "\n✨ • • • • • • ✨\n", "\n▬ ▬ ▬ ▬ ▬ ▬ ▬\n", "\n────────────────\n"]
    return random.choice(dividers)

def get_full_currency():
    res = "💰 **КУРС ВАЛЮТ**\n"
    try:
        p = requests.get("https://api.privatbank.ua/p24api/pubinfo?exchange&json&coursid=11", timeout=10).json()
        usd = next(i for i in p if i['ccy'] == 'USD')
        eur = next(i for i in p if i['ccy'] == 'EUR')
        res += f"🏦 Приват: 🇺🇸{usd['buy'][:5]}/{usd['sale'][:5]} | 🇪🇺{eur['buy'][:5]}/{eur['sale'][:5]}\n"
    except: res += "🏦 Приват: Оновлюється...\n"
    try:
        m = requests.get("https://api.monobank.ua/bank/currency", timeout=10).json()
        u = next(i for i in m if i['currencyCodeA'] == 840 and i['currencyCodeB'] == 980)
        e = next(i for i in m if i['currencyCodeA'] == 978 and i['currencyCodeB'] == 980)
        res += f"🐱 Моно: 🇺🇸{u['rateBuy']}/{u['rateSell']} | 🇪🇺{e['rateBuy']}/{e['rateSell']}\n"
    except: res += "🐱 Моно: Оновлюється...\n"
    return res

def get_holidays():
    now = datetime.datetime.now()
    url = f"https://holidays.abstractapi.com/v1/?api_key={HOLIDAY_API_KEY}&country=UA&year={now.year}&month={now.month}&day={now.day}"
    try:
        r = requests.get(url, timeout=10).json()
        if r and isinstance(r, list):
            return "🎊 **СВЯТА:** " + ", ".join([h['name'] for h in r])
        return "🎊 **СВЯТА:** Офіційних свят немає"
    except: return "🎊 **СВЯТА:** Не вдалося завантажити"

def get_movie():
    try:
        r = requests.get(f"https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}&language=uk-UA&page={random.randint(1, 10)}", timeout=10).json()
        m = random.choice(r['results'])
        return f"🎬 **КІНОЗАЛ**\n🎥 **{m['title']}**\n⭐ {m['vote_average']}\n🍿 {m['overview'][:200]}..."
    except: return "🎬 Подивіться щось цікаве сьогодні!"

def get_line(file):
    try:
        with open(file, 'r', encoding='utf-8') as f:
            lines = [l.strip() for l in f.readlines() if l.strip()]
            return random.choice(lines) if lines else "Дані відсутні"
    except: return f"Файл {file} не знайдено"

def make_post():
    # Визначаємо тип поста за часом (UTC)
    hour = (datetime.datetime.now().hour + 2) % 24 # Корекція на час України
    
    if 5 <= hour < 11: # Ранок
        today = datetime.date.today()
        ny = datetime.date(today.year + (1 if today.month == 12 and today.day > 31 else 0), 1, 1)
        return (f"🌅 **РАНОК**\n📅 {today.strftime('%d.%m.%Y')}\n{get_divider()}"
                f"🎂 Іменини: {get_line('names.txt')}\n{get_holidays()}\n📜 Історія: {get_line('history.txt')}\n"
                f"{get_divider()}{get_full_currency()}\n🎄 До НР: {(ny-today).days} дн.\n"
                f"{get_divider()}💡 Лайфхак: {get_line('advices.txt')}")
    
    elif 11 <= hour < 18: # День
        return f"🌤 **ДЕНЬ**\n\n💡 Лайфхак: {get_line('advices.txt')}\n{get_divider()}🧐 Факт: {get_line('facts.txt')}"
    
    else: # Вечір
        return (f"🌙 **ВЕЧІР**\n\n💡 Лайфхак: {get_line('advices.txt')}\n{get_divider()}"
                f"🧐 Факт: {get_line('facts.txt')}\n{get_divider()}😂 Жарт: {get_line('jokes.txt')}\n"
                f"{get_divider()}{get_movie()}")

if __name__ == "__main__":
    print(make_post())
