import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_data():
    h = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'}
    
    # --- 🏛 НБУ (XML-фід) ---
    nbu = "немає даних"
    try:
        # Використовуємо XML посилання, яке ти надав
        r = requests.get("https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange", timeout=15)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'xml') # Використовуємо xml парсер
            # Шукаємо валюту за кодом (USD = 840, EUR = 978) або по CC
            usd_rate = soup.find('currency', {'cc': 'USD'}).find('rate').text
            eur_rate = soup.find('currency', {'cc': 'EUR'}).find('rate').text
            nbu = f"🇺🇸 {float(usd_rate):.2f} | 🇪🇺 {float(eur_rate):.2f}"
    except: pass

    # --- 🏦 РАЙФФАЙЗЕН ---
    raif = "н/д"
    try:
        r_raif = requests.get("https://raiffeisen.ua/currency", headers=h, timeout=15)
        soup = BeautifulSoup(r_raif.text, 'html.parser')
        # На сайті Райфу курси в дивах з класом currency-table__body-cell
        cells = soup.find_all('div', class_='currency-table__body-cell')
        if len(cells) >= 6:
            u_b, u_s = cells[1].text.strip(), cells[2].text.strip()
            e_b, e_s = cells[4].text.strip(), cells[5].text.strip()
            raif = f"🇺🇸 {u_b}/{u_s} | 🇪🇺 {e_b}/{e_s}"
    except: pass

    # --- 🏦 ПУМБ ---
    pumb = "н/д"
    try:
        r_pumb = requests.get("https://about.pumb.ua/info/currency_converter", headers=h, timeout=15)
        soup = BeautifulSoup(r_pumb.text, 'html.parser')
        # Шукаємо в таблицях
        rows = soup.find_all('tr')
        usd, eur = "", ""
        for row in rows:
            t = row.get_text()
            tds = [td.get_text(strip=True) for td in row.find_all('td')]
            if "USD" in t and len(tds) >= 3:
                usd = f"{tds[1]}/{tds[2]}"
            if "EUR" in t and len(tds) >= 3:
                eur = f"{tds[1]}/{tds[2]}"
        if usd and eur: pumb = f"🇺🇸 {usd} | 🇪🇺 {eur}"
    except: pass

    # --- ⛽ ПАЛЬНЕ (Живий парсинг середніх цін) ---
    fuel = "🔹 Дані тимчасово недоступні"
    try:
        r_f = requests.get("https://index.minfin.com.ua/ua/fuel/average/", headers=h, timeout=15)
        soup = BeautifulSoup(r_f.text, 'html.parser')
        table = soup.find('table', class_='list')
        f_list = []
        for row in table.find_all('tr')[1:4]: # А-95, ДП, Газ
            tds = row.find_all('td')
            if len(tds) >= 2:
                f_list.append(f"🔹 {tds[0].text.strip()}: {tds[1].text.strip()} грн")
        fuel = "\n".join(f_list)
    except: pass

    return nbu, raif, pumb, fuel

def get_git_info(file, key):
    url = f"https://raw.githubusercontent.com/savchinviktorm-create/my-daily-bot/main/{file}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            lines = r.content.decode('utf-8').splitlines()
            for line in lines:
                if key in line: return line.split('—', 1)[-1].strip()
    except: pass
    return "дані відсутні"

def send():
    nbu, raif, pumb, fuel = get_data()
    now = datetime.now()
    
    # Назви місяців
    m_list = ["січня","лютого","березня","квітня","травня","червня","липня","серпня","вересня","жовтня","листопада","грудня"]
    day_str = f"{now.day} {m_list[now.month-1]}"

    msg = (
        f"📅 **ЗВІТ НА {now.strftime('%d.%m.%Y')}**\n\n"
        f"🏛 **КУРС НБУ:**\n{nbu}\n\n"
        f"🏦 **КУРСИ БАНКІВ:**\n"
        f"• Райффайзен: {raif}\n"
        f"• ПУМБ: {pumb}\n\n"
        f"⛽ **ЦІНИ НА ПАЛЬНЕ:**\n{fuel}\n\n"
        f"😇 **Іменини:** {get_git_info('names.txt', day_str)}\n"
        f"📜 **Історія:** {get_git_info('history.txt', now.strftime('%m-%d'))}\n\n"
        f"🎄 До Нового року: {(datetime(now.year + 1, 1, 1) - now).days} днів!"
    )

    requests.post(f"https://api.telegram.org/bot{os.getenv('TOKEN')}/sendMessage", 
                  json={"chat_id": os.getenv('MY_CHAT_ID'), "text": msg, "parse_mode": "Markdown"})

if __name__ == "__main__":
    send()
