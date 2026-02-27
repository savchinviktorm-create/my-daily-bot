import os
import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime

def get_content(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept-Language': 'uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7'
    }
    try:
        r = requests.get(url, headers=headers, timeout=20)
        return r.text
    except: return ""

def parse_currency():
    html = get_content("https://minfin.com.ua/ua/currency/")
    res = {"usd": "немає даних", "eur": "немає даних", "u_val": 0.0, "e_val": 0.0}
    if not html: return res
    
    # Шукаємо курси за допомогою регулярних виразів прямо в тексті
    usd = re.findall(r'USD.*?(\d+,\d+).*?(\d+,\d+)', html, re.DOTALL)
    eur = re.findall(r'EUR.*?(\d+,\d+).*?(\d+,\d+)', html, re.DOTALL)
    
    if usd:
        res["usd"] = f"{usd[0][0]} / {usd[0][1]}"
        res["u_val"] = float(usd[0][0].replace(',', '.'))
    if eur:
        res["eur"] = f"{eur[0][0]} / {eur[0][1]}"
        res["e_val"] = float(eur[0][0].replace(',', '.'))
    return res

def parse_fuel():
    html = get_content("https://index.minfin.com.ua/ua/markets/fuel/")
    fuel = {"a95": "н/д", "dp": "н/д", "gas": "н/д"}
    if not html: return fuel
    
    soup = BeautifulSoup(html, 'html.parser')
    rows = soup.find_all('tr')
    for row in rows:
        t = row.text
        if "A-95" in t and "Плюс" not in t:
            fuel["a95"] = row.find_all('td')[1].text.strip()
        elif "ДП" in t:
            fuel["dp"] = row.find_all('td')[1].text.strip()
        elif "Газ" in t:
            fuel["gas"] = row.find_all('td')[1].text.strip()
    return fuel

def get_git_info(file, key):
    try:
        r = requests.get(f"https://raw.githubusercontent.com/savchinviktorm-create/my-daily-bot/main/{file}")
        if r.status_code == 200:
            lines = r.text.splitlines()
            for line in lines:
                if key.lower() in line.lower():
                    return line.split('—')[-1].strip() if '—' in line else line.strip()
    except: pass
    return "дані відсутні"

def send():
    curr = parse_currency()
    fuel = parse_fuel()
    now = datetime.now()
    
    cross = round(curr['e_val'] / curr['u_val'], 3) if curr['u_val'] > 0 else "н/д"
    
    m_ukr = ["січня","лютого","березня","квітня","травня","червня","липня","серпня","вересня","жовтня","листопада","грудня"]
    day_name = f"{now.day} {m_ukr[now.month-1]}"
    day_hist = now.strftime("%m-%d") # Спробуємо такий формат для історії

    msg = (
        f"📅 **ЗВІТ НА {now.strftime('%d.%m.%Y')}**\n\n"
        f"💰 **Курс валют (Мінфін):**\n🇺🇸 USD: {curr['usd']}\n🇪🇺 EUR: {curr['eur']}\n💱 Крос-курс: {cross}\n\n"
        f"⛽ **Пальне:**\n🔹 А-95: {fuel['a95']} грн\n🔹 ДП: {fuel['dp']} грн\n🔹 Газ: {fuel['gas']} грн\n\n"
        f"😇 **Іменини:** {get_git_info('names.txt', day_name)}\n"
        f"📜 **Історія:** {get_git_info('history.txt', day_hist)}\n\n"
        f"🎄 До Нового року: {(datetime(now.year + 1, 1, 1) - now).days} днів!"
    )

    requests.post(f"https://api.telegram.org/bot{os.getenv('TOKEN')}/sendMessage", 
                  json={"chat_id": os.getenv('MY_CHAT_ID'), "text": msg, "parse_mode": "Markdown"})

if __name__ == "__main__":
    send()
