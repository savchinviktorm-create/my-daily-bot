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

def parse_data():
    # 1. ВАЛЮТИ (finance.i.ua)
    res = {"usd": "н/д", "eur": "н/д", "u_val": 0.0, "e_val": 0.0}
    soup_curr = get_soup("https://finance.i.ua/")
    if soup_curr:
        table = soup_curr.find('table', class_='table-delta')
        if table:
            rows = table.find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 3:
                    # Шукаємо саме тег <span class="value">, щоб не брати індекси зміни курсу
                    buy_span = cols[1].find('span', class_='value')
                    sale_span = cols[2].find('span', class_='value')
                    
                    if buy_span and sale_span:
                        buy = buy_span.get_text(strip=True).replace(',', '.')
                        sale = sale_span.get_text(strip=True).replace(',', '.')
                        
                        name = cols[0].get_text().upper()
                        if "USD" in name:
                            res["usd"] = f"{buy} / {sale}"
                            res["u_val"] = float(buy)
                        elif "EUR" in name:
                            res["eur"] = f"{buy} / {sale}"
                            res["e_val"] = float(buy)

    # 2. ПАЛЬНЕ (finance.i.ua/fuel/)
    fuel = {"a95": "н/д", "dp": "н/д", "gas": "н/д"}
    soup_fuel = get_soup("https://finance.i.ua/fuel/")
    if soup_fuel:
        # Шукаємо рядок "Середня" в таблиці
        for row in soup_fuel.find_all('tr'):
            cells = row.find_all(['td', 'th'])
            row_text = row.get_text()
            if "Середня" in row_text and len(cells) >= 4:
                fuel["a95"] = cells[2].get_text(strip=True)
                fuel["dp"] = cells[3].get_text(strip=True)
            if "Газ" in row_text and len(cells) >= 2 and fuel["gas"] == "н/д":
                fuel["gas"] = cells[1].get_text(strip=True)
                
    return res, fuel

def get_git_info(file, key):
    url = f"https://raw.githubusercontent.com/savchinviktorm-create/my-daily-bot/main/{file}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            for line in r.text.splitlines():
                if key in line:
                    return line.split('—', 1)[-1].strip()
    except: pass
    return "немає даних"

def send():
    curr, fuel = parse_data()
    now = datetime.now()
    
    # Крос-курс по купівлі
    cross = round(curr['e_val'] / curr['u_val'], 2) if curr['u_val'] > 0 else "н/д"
    
    m_ukr = ["січня","лютого","березня","квітня","травня","червня","липня","серпня","вересня","жовтня","листопада","грудня"]
    day_name = f"{now.day} {m_ukr[now.month-1]}"
    day_hist = now.strftime("%m-%d")

    msg = (
        f"📅 **ЗВІТ НА {now.strftime('%d.%m.%Y')}**\n\n"
        f"💰 **Курс (finance.i.ua):**\n🇺🇸 USD: {curr['usd']}\n🇪🇺 EUR: {curr['eur']}\n💱 Крос-курс: {cross}\n\n"
        f"⛽ **Середні ціни на пальне:**\n🔹 А-95: {fuel['a95']} грн\n🔹 ДП: {fuel['dp']} грн\n🔹 Газ: {fuel['gas']} грн\n\n"
        f"😇 **Іменини:** {get_git_info('names.txt', day_name)}\n"
        f"📜 **Історія:** {get_git_info('history.txt', day_hist)}\n\n"
        f"🎄 До Нового року: {(datetime(now.year + 1, 1, 1) - now).days} днів!"
    )

    requests.post(f"https://api.telegram.org/bot{os.getenv('TOKEN')}/sendMessage", 
                  json={"chat_id": os.getenv('MY_CHAT_ID'), "text": msg, "parse_mode": "Markdown"})

if __name__ == "__main__":
    send()
