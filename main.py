import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_data():
    h = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'}
    
    # --- 🏛 НБУ (Офіційний курс) ---
    nbu = "немає даних"
    try:
        # Отримуємо JSON. НБУ тепер додає поле 'special', ігноруємо його
        r = requests.get("https://bank.gov.ua/NBUStatService/v1/statistictic/exchange?json", timeout=15)
        if r.status_code == 200:
            data = r.json()
            u = next(i['rate'] for i in data if i['cc'] == 'USD')
            e = next(i['rate'] for i in data if i['cc'] == 'EUR')
            nbu = f"🇺🇸 {u:.2f} | 🇪🇺 {e:.2f}"
    except: pass

    # --- 🏦 РАЙФФАЙЗЕН (raiffeisen.ua/currency) ---
    raif = "н/д"
    try:
        r_raif = requests.get("https://raiffeisen.ua/currency", headers=h, timeout=15)
        soup = BeautifulSoup(r_raif.text, 'html.parser')
        # Знаходимо значення через класи таблиці
        vals = soup.find_all('div', class_='currency-table__body-cell')
        # Зазвичай: 0-USD, 1-Купівля, 2-Продаж
        u_b, u_s = vals[1].text.strip(), vals[2].text.strip()
        e_b, e_s = vals[4].text.strip(), vals[5].text.strip()
        raif = f"🇺🇸 {u_b}/{u_s} | 🇪🇺 {e_b}/{e_s}"
    except: pass

    # --- 🏦 ПУМБ (about.pumb.ua/info/currency_converter) ---
    pumb = "н/д"
    try:
        r_pumb = requests.get("https://about.pumb.ua/info/currency_converter", headers=h, timeout=15)
        soup = BeautifulSoup(r_pumb.text, 'html.parser')
        # Шукаємо в таблиці конвертера
        rows = soup.find_all('tr')
        p_data = {}
        for row in rows:
            if "USD" in row.text: p_data['usd'] = [td.text.strip() for td in row.find_all('td')]
            if "EUR" in row.text: p_data['eur'] = [td.text.strip() for td in row.find_all('td')]
        pumb = f"🇺🇸 {p_data['usd'][1]}/{p_data['usd'][2]} | 🇪🇺 {p_data['eur'][1]}/{p_data['eur'][2]}"
    except: pass

    # --- ⛽ ПАЛЬНЕ (Середні ціни) ---
    fuel = "🔹 Дані тимчасово недоступні"
    try:
        # Беремо з Мінфіну, бо це найнадійніше джерело середніх цін
        r_f = requests.get("https://index.minfin.com.ua/ua/fuel/average/", headers=h, timeout=15)
        soup = BeautifulSoup(r_f.text, 'html.parser')
        table = soup.find('table', class_='list')
        f_list = []
        for row in table.find_all('tr')[1:4]: # А-95, ДП, Газ
            tds = row.find_all('td')
            f_list.append(f"🔹 {tds[0].text.strip()}: {tds[1].text.strip()} грн")
        fuel = "\n".join(f_list)
    except: pass

    return nbu, raif, pumb, fuel

def send():
    nbu, raif, pumb, fuel = get_data()
    # Приват та Моно додаємо через швидкі API для надійності
    pb, mn = "н/д", "н/д"
    try:
        pb_data = requests.get("https://api.privatbank.ua/p24api/pubinfo?exchange&coursid=5").json()
        u = next(i for i in pb_data if i['ccy'] == 'USD')
        pb = f"{float(u['buy']):.2f}/{float(u['sale']):.2f}"
        
        mn_data = requests.get("https://api.monobank.ua/bank/currency").json()
        u = next(i for i in mn_data if i['currencyCodeA'] == 840 and i['currencyCodeB'] == 980)
        mn = f"{u['rateBuy']:.2f}/{u['rateSell']:.2f}"
    except: pass

    now = datetime.now()
    msg = (
        f"📅 **ЗВІТ НА {now.strftime('%d.%m.%Y')}**\n\n"
        f"🏛 **КУРС НБУ:**\n{nbu}\n\n"
        f"🏦 **КУРСИ БАНКІВ:**\n"
        f"• Приват: {pb}\n"
        f"• Моно: {mn}\n"
        f"• Райффайзен: {raif}\n"
        f"• ПУМБ: {pumb}\n\n"
        f"⛽ **ЦІНИ НА ПАЛЬНЕ:**\n{fuel}\n\n"
        f"🎄 До Нового року: {(datetime(now.year + 1, 1, 1) - now).days} днів!"
    )

    requests.post(f"https://api.telegram.org/bot{os.getenv('TOKEN')}/sendMessage", 
                  json={"chat_id": os.getenv('MY_CHAT_ID'), "text": msg, "parse_mode": "Markdown"})

if __name__ == "__main__":
    send()
