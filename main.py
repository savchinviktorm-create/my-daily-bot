import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_soup(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    try:
        r = requests.get(url, headers=headers, timeout=15)
        r.encoding = 'utf-8'
        return BeautifulSoup(r.text, 'html.parser')
    except: return None

def parse_currency():
    soup = get_soup("https://minfin.com.ua/ua/currency/")
    res = {"usd": "немає даних", "eur": "немає даних", "u_val": 0.0, "e_val": 0.0}
    if not soup: return res
    
    table = soup.find('table', class_='mfcur-table-bank')
    if table:
        for row in table.find_all('tr'):
            txt = row.get_text().upper()
            cols = row.find_all('td')
            if len(cols) >= 2:
                # Очищуємо текст від зайвого сміття та пробілів
                raw_val = cols[1].get_text(separator=" ", strip=True).split()
                if len(raw_val) >= 2:
                    buy, sale = raw_val[0], raw_val[1]
                    if "USD" in txt:
                        res["usd"] = f"{buy} / {sale}"
                        res["u_val"] = float(buy.replace(',', '.'))
                    elif "EUR" in txt:
                        res["eur"] = f"{buy} / {sale}"
                        res["e_val"] = float(buy.replace(',', '.'))
    return res

def parse_fuel():
    soup = get_soup("https://index.minfin.com.ua/ua/markets/fuel/")
    fuel = {"a95": "н/д", "dp": "н/д", "gas": "н/д"}
    if not soup: return fuel
    
    table = soup.find('table', class_='list')
    if table:
        for row in table.find_all('tr'):
            cols = row.find_all('td')
            if len(cols) >= 2:
                name = cols[0].get_text(strip=True)
                price = cols[1].get_text(strip=True)
                if name == "A-95": fuel["a95"] = price
                elif name == "ДП": fuel["dp"] = price
                elif name == "Газ": fuel["gas"] = price
    return fuel

def get_git_info(file, key):
    url = f"https://raw.githubusercontent.com/savchinviktorm-create/my-daily-bot/main/{file}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            for line in r.text.splitlines():
                if key.lower() in line.lower():
                    return line.split('—')[-1].strip() if '—' in line else line.strip()
    except: pass
    return "дані відсутні"

def send():
    c = parse_currency()
    f = parse_fuel()
    now = datetime.now()
    
    cross = round(c['e_val'] / c['u_val'], 3) if c['u_val'] > 0 else "н/д"
    
    m_ukr = ["січня","лютого","березня","квітня","травня","червня","липня","серпня","вересня","жовтня","листопада","грудня"]
    day_name = f"{now.day} {m_ukr[now.month-1]}" # Наприклад: "27 лютого"
    day_hist = now.strftime("%m-%d")            # Наприклад: "02-27"

    msg = (
        f"📅 **ЗВІТ НА {now.strftime('%d.%m.%Y')}**\n\n"
        f"💰 **Курс валют (Мінфін):**\n🇺🇸 USD: {c['usd']}\n🇪🇺 EUR: {c['eur']}\n💱 Крос-курс: {cross}\n\n"
        f"⛽ **Пальне (Середні ціни):**\n🔹 А-95: {f['a95']} грн\n🔹 ДП: {f['dp']} грн\n🔹 Газ: {f['gas']} грн\n\n"
        f"😇 **Іменини:** {get_git_info('names.txt', day_name)}\n"
        f"📜 **Історія:** {get_git_info('history.txt', day_hist)}\n\n"
        f"🎄 До Нового року: {(datetime(now.year + 1, 1, 1) - now).days} днів!"
    )

    requests.post(f"https://api.telegram.org/bot{os.getenv('TOKEN')}/sendMessage", 
                  json={"chat_id": os.getenv('MY_CHAT_ID'), "text": msg, "parse_mode": "Markdown"})

if __name__ == "__main__":
    send()
