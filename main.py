import os
import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime

def get_soup(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'}
    try:
        r = requests.get(url, headers=headers, timeout=15)
        r.encoding = 'utf-8'
        return BeautifulSoup(r.text, 'html.parser')
    except: return None

def parse_currency():
    soup = get_soup("https://minfin.com.ua/ua/currency/")
    res = {"usd": "немає даних", "eur": "немає даних", "u_val": 0.0, "e_val": 0.0}
    if not soup: return res
    
    # Шукаємо таблицю середніх курсів
    table = soup.find('table', class_='mfcur-table-bank')
    if table:
        rows = table.find_all('tr')
        for row in rows:
            row_text = row.text.upper()
            cols = row.find_all('td')
            if len(cols) >= 2:
                # Витягуємо числа (купівля та продаж)
                vals = re.findall(r'\d+,\d+', cols[1].text)
                if "USD" in row_text and len(vals) >= 2:
                    res["usd"] = f"{vals[0]} / {vals[1]}"
                    res["u_val"] = float(vals[0].replace(',', '.'))
                elif "EUR" in row_text and len(vals) >= 2:
                    res["eur"] = f"{vals[0]} / {vals[1]}"
                    res["e_val"] = float(vals[0].replace(',', '.'))
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
                name = cols[0].text.strip()
                price = cols[1].text.strip()
                if name == "A-95": fuel["a95"] = price
                elif name == "ДП": fuel["dp"] = price
                elif name == "Газ": fuel["gas"] = price
    return fuel

def get_git_info(file_name, key):
    url = f"https://raw.githubusercontent.com/savchinviktorm-create/my-daily-bot/main/{file_name}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            for line in r.text.splitlines():
                if key.lower() in line.lower():
                    return line.split('—', 1)[-1].strip() if '—' in line else line.strip()
    except: pass
    return "немає даних"

def send_report():
    curr = parse_currency()
    fuel = parse_fuel()
    now = datetime.now()
    
    # Крос-курс (ділимо купівлю євро на купівлю долара)
    cross = round(curr['e_val'] / curr['u_val'], 3) if curr['u_val'] > 0 else "н/д"
    
    months = ["січня", "лютого", "березня", "квітня", "травня", "червня", "липня", "серпня", "вересня", "жовтня", "листопада", "грудня"]
    day_name = f"{now.day} {months[now.month-1]}" # Для іменин: "27 лютого"
    day_str = now.strftime("%d.%m") # Для історії: "27.02"

    msg = (
        f"📅 **ЗВІТ НА {now.strftime('%d.%m.%Y')}**\n\n"
        f"💰 **Курс валют (Мінфін):**\n"
        f"🇺🇸 USD: {curr['usd']}\n"
        f"🇪🇺 EUR: {curr['eur']}\n"
        f"💱 Крос-курс: {cross}\n\n"
        f"⛽ **Ціни на пальне (Середні):**\n"
        f"🔹 А-95: {fuel['a95']} грн\n"
        f"🔹 ДП: {fuel['dp']} грн\n"
        f"🔹 Газ: {fuel['gas']} грн\n\n"
        f"😇 **Іменини:** {get_git_info('names.txt', day_name)}\n"
        f"📜 **Історія:** {get_git_info('history.txt', day_str)}\n\n"
        f"🎄 До Нового року: {(datetime(now.year + 1, 1, 1) - now).days} днів!"
    )

    token = os.getenv('TOKEN')
    chat_id = os.getenv('MY_CHAT_ID')
    requests.post(f"https://api.telegram.org/bot{token}/sendMessage", 
                  json={"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"})

if __name__ == "__main__":
    send_report()
