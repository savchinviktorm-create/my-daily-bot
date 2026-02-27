import os
import urllib.request
import json
import csv
import io
import re
from datetime import datetime

# Посилання залишається те саме
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSExxHF9GN-lpJF9I3L9kLzFoH9lo4_emwtiEoHpiezlf3ESOw6dxGrjmQwk1wuFC6mV6035wu6-l4M/pub?gid=2060076239&single=true&output=csv"

def get_data_from_file(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=20) as r:
            # Читаємо як байти і декодуємо в utf-8, ігноруючи помилки
            content = r.read()
            return content.decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Завантаження не вдалося: {e}")
        return None

def parse_everything():
    raw_text = get_data_from_file(URL_CSV)
    if not raw_text:
        return None

    # Використовуємо StringIO для імітації файлу в пам'яті
    f = io.StringIO(raw_text)
    reader = csv.reader(f)
    
    results = {
        "USD_BUY": "0.00", "USD_SALE": "0.00",
        "EUR_BUY": "0.00", "EUR_SALE": "0.00",
        "A95": "0.00", "DP": "0.00", "GAS": "0.00"
    }

    for row in reader:
        # Очищаємо рядок від зайвого
        row_str = "|".join([c.strip() for c in row if c.strip()])
        if not row_str: continue

        # Шукаємо всі числа в рядку через регулярні вирази
        # Це витягне ['56', '1500'] навіть якщо вони в різних клітинках
        nums = re.findall(r'\d+', row_str)

        # Логіка визначення що це за рядок
        if "USD" in row_str.upper() and len(nums) >= 4:
            results["USD_BUY"] = f"{nums[0]}.{nums[1][:2]}"
            results["USD_SALE"] = f"{nums[2]}.{nums[3][:2]}"
        
        elif "EUR" in row_str.upper() and len(nums) >= 4:
            results["EUR_BUY"] = f"{nums[0]}.{nums[1][:2]}"
            results["EUR_SALE"] = f"{nums[2]}.{nums[3][:2]}"
        
        elif "А-95" in row_str and len(nums) >= 2:
            results["A95"] = f"{nums[0]}.{nums[1][:2]}"
        
        elif "ДП" in row_str and len(nums) >= 2:
            results["DP"] = f"{nums[0]}.{nums[1][:2]}"
        
        elif "Газ" in row_str and len(nums) >= 2:
            results["GAS"] = f"{nums[0]}.{nums[1][:2]}"

    return results

def send_final_report():
    data = parse_everything()
    if not data:
        print("Не вдалося отримати дані з таблиці")
        return

    now = datetime.now()
    # Математичний крос-курс (чистий розрахунок)
    try:
        cross = round(float(data["EUR_BUY"]) / float(data["USD_BUY"]), 3) if float(data["USD_BUY"]) > 0 else 0
    except: cross = "н/д"

    msg = (
        f"📅 **ЗВІТ НА {now.strftime('%d.%m.%Y')}**\n\n"
        f"💰 **Курс валют (Мінфін):**\n"
        f"🇺🇸 USD: {data['USD_BUY']} / {data['USD_SALE']}\n"
        f"🇪🇺 EUR: {data['EUR_BUY']} / {data['EUR_SALE']}\n"
        f"💱 Крос-курс: {cross}\n\n"
        f"⛽ **Ціни на пальне (Мінфін):**\n"
        f"🔹 А-95: {data['A95']} грн\n"
        f"🔹 ДП: {data['DP']} грн\n"
        f"🔹 Газ: {data['GAS']} грн\n\n"
        f"🎄 До Нового року: {(datetime(now.year + 1, 1, 1) - now).days} днів!"
    )

    token = os.getenv('TOKEN')
    chat_id = os.getenv('MY_CHAT_ID')
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = json.dumps({"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"}).encode('utf-8')
    req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})
    urllib.request.urlopen(req)

if __name__ == "__main__":
    send_final_report()
    
