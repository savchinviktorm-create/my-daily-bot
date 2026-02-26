import os
import urllib.request
import urllib.parse
import json

def send_msg(token, chat_id, text):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode({'chat_id': chat_id, 'text': text}).encode()
    urllib.request.urlopen(urllib.request.Request(url, data=data))

# Беремо секрети
token = os.environ.get("TOKEN", "").strip()
chat_id = os.environ.get("MY_CHAT_ID", "").strip()

try:
    # Пробуємо просто надіслати "Привіт", щоб перевірити зв'язок
    send_msg(token, chat_id, "🚀 Г'юстон, у нас є зв'язок! Бот працює!")
    print("DONE")
except Exception as e:
    print(f"ERROR: {e}")
    exit(1)
