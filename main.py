import os
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

def get_data(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    try:
        r = requests.get(url, headers=headers, timeout=15)
        r.encoding = 'utf-8'
        return r.text
    except: return ""

def parse_all():
    # Парсимо валюти
    html_curr = get_data("https://finance.i.ua/")
    res = {"usd": "н/д", "eur": "н/д", "u_val": 1.0, "e_val": 1.0}
    
    # Шукаємо блоки з валютами по тексту
    usd_match = re.search(r'USD.*?(\d+\.\d+).*?(\d+\.\d+)', html_curr, re.DOTALL)
    eur_match = re.search(r'EUR.*?(\d+\.\d+).*?(\d+\.\d+)', html_curr, re.DOTALL)
    
    if usd_match:
        res["usd"] = f"{usd_match.group(1)} / {usd_match.group(2)}"
        res["u_val"] = float(usd_match.group(1))
    if eur_match:
        res["eur"] = f"{eur_match.group(1)} / {eur_match.group(2)}"
        res["e_val"] = float(eur_match.group(1))

    # Парсимо пальне (середні ціни з таблиці внизу сторінки)
    html_fuel = get_data("https://finance.i.ua/fuel/")
    fuel = {"a95": "н/д", "dp": "н/д"}
    
    if html_fuel:
        soup = BeautifulSoup(html_fuel, 'lxml')
        # Шукаємо рядок "Середня"
        for row in soup.find_all('tr'):
            if "Середня" in row.text:
                tds = row.find_all('td')
                if len(tds) >= 4:
                    fuel["a95"] = tds[2].get_text(strip=True)
                    fuel["dp"] = tds[3].get_text(strip=True)
    return res, fuel

def get_git_info(file, key):
    url = f"https://raw.githubusercontent.com/savchinviktorm-create/my-daily-bot/main/{file}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            lines = r.text.splitlines()
            for line in lines:
                if key in line:
                    return line.split('—')[-1].strip() if '—' in line else line.strip()
    except: pass
    return "немає в базі"

def send():
    curr, fuel = parse_all()
    now = datetime.now()
    
    # Крос-курс
    cross = round(curr['e_val'] / curr['u_val'], 3) if curr['u_val'] > 0 else "н/д"
    
    # Дати для пошуку в твоїх файлах
    m_list = ["січня","лютого","березня","квітня","травня","червня","липня","серпня","вересня","жовтня","листопада","грудня"]
    day_name = f"{now.day} {m_list[now.month-1]}" # "27 лютого"
    day_hist = now.strftime("%m-%d")            # "02-27"

    msg = (
        f"📅 **ЗВІТ НА {now.strftime('%d.%m.%Y')}**\n\n"
        f"💰 **Курс (i.ua):**\n🇺🇸 USD: {curr['usd']}\n🇪🇺 EUR: {curr['eur']}\n💱 Крос-курс: {cross}\n\n"
        f"⛽ **Пальне (Середні):**\n🔹 А-95: {fuel['a95']} грн\n🔹 ДП: {fuel['dp']} грн\n\n"
        f"😇 **Іменини:** {get_git_info('names.txt', day_name)}\n"
        f"📜 **Історія:** {get_git_info('history.txt', day_hist)}\n\n"
        f"🎄 До Нового року: {(datetime(now.year + 1, 1, 1) - now).days} днів!"
    )

    requests.post(f"https://api.telegram.org/bot{os.getenv('TOKEN')}/sendMessage", 
                  json={"chat_id": os.getenv('MY_CHAT_ID'), "text": msg, "parse_mode": "Markdown"})

if __name__ == "__main__":
    send()
