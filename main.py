import requests
import random
import datetime

# --- НАЛАШТУВАННЯ ТА КЛЮЧІ (ВСТАВЛЕНО З ТВОЇХ СКРІНШОТІВ) ---
TMDB_API_KEY = "583e99233cb332aaf8ab0ded7a92dde7"
HOLIDAY_API_KEY = "17904126938947f694726e6423985558" # Ключ з Abstract API

# --- ГЕНЕРАТОР РІЗНОМАНІТНИХ РОЗДІЛЮВАЧІВ ---
def get_divider():
    dividers = [
        "\n━━━━━━━━━━━━━━━━━━━━━━\n",
        "\n✨ • • • • • • • • • • • ✨\n",
        "\n▬ ▬ ▬ ▬ ▬ ▬ ▬ ▬ ▬ ▬ ▬ ▬\n",
        "\n🔹 🔹 🔹 🔹 🔹 🔹 🔹 🔹 🔹 🔹\n",
        "\n──────────────────────\n",
        "\n◈━━━━━━━━━━━━━━━━━━━━◈\n",
        "\n🌿 ━━━━━━━━━━━━━━━━━━ 🌿\n"
    ]
    return random.choice(dividers)

# --- МОДУЛЬ ВАЛЮТ (ПРИВАТ + МОНО) ---
def get_full_currency():
    res_text = "💰 **КУРС ВАЛЮТ**\n"
    # ПриватБанк
    try:
        p_api = requests.get("https://api.privatbank.ua/p24api/pubinfo?exchange&json&coursid=11", timeout=8).json()
        usd_p = next(i for i in p_api if i['ccy'] == 'USD')
        eur_p = next(i for i in p_api if i['ccy'] == 'EUR')
        res_text += f"🏦 Приват: 🇺🇸{usd_p['buy'][:5]}/{usd_p['sale'][:5]} | 🇪🇺{eur_p['buy'][:5]}/{eur_p['sale'][:5]}\n"
    except:
        res_text += "🏦 Приват: Сервіс недоступний\n"

    # Монобанк
    try:
        m_api = requests.get("https://api.monobank.ua/bank/currency", timeout=8).json()
        usd_m = next(i for i in m_api if i['currencyCodeA'] == 840 and i['currencyCodeB'] == 980)
        eur_m = next(i for i in m_api if i['currencyCodeA'] == 978 and i['currencyCodeB'] == 980)
        res_text += f"🐱 Моно: 🇺🇸{usd_m['rateBuy']}/{usd_m['rateSell']} | 🇪🇺{eur_m['rateBuy']}/{eur_m['rateSell']}\n"
    except:
        res_text += "🐱 Моно: Оновлюється...\n"
    
    return res_text

# --- МОДУЛЬ СВЯТ (ABSTRACT API) ---
def get_holidays():
    now = datetime.datetime.now()
    url = f"https://holidays.abstractapi.com/v1/?api_key={HOLIDAY_API_KEY}&country=UA&year={now.year}&month={now.month}&day={now.day}"
    try:
        response = requests.get(url, timeout=8).json()
        if response and isinstance(response, list):
            holidays = [h['name'] for h in response]
            return "🎊 **СВЯТА:** " + ", ".join(holidays)
        return "🎊 **СВЯТА:** Офіційних свят сьогодні немає"
    except:
        return "🎊 **СВЯТА:** Інформація тимчасово відсутня"

# --- МОДУЛЬ КІНО (TMDB) ---
def get_movie():
    page = random.randint(1, 15)
    url = f"https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}&language=uk-UA&page={page}"
    try:
        data = requests.get(url, timeout=8).json()
        movie = random.choice(data['results'])
        title = movie.get('title', 'Цікавий фільм')
        rating = movie.get('vote_average', '7.5')
        desc = movie.get
