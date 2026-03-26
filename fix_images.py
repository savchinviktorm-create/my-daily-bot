import os
import time
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image

def optimize_folder():
    # Створюємо вікно і ховаємо зайве
    root = tk.Tk()
    root.withdraw()

    # Відкриваємо вікно вибору папки
    target_dir = filedialog.askdirectory(title="Оберіть папку з картинками для Вайбера")
    
    if not target_dir:
        return

    MAX_SIZE = 950
    count = 0

    for root_dir, _, files in os.walk(target_dir):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in ['.png', '.jpg', '.jpeg', '.webp', '.bmp', '.jfif']:
                filepath = os.path.join(root_dir, file)
                try:
                    file_size = os.path.getsize(filepath) / 1024
                    
                    # Якщо це вже нормальний JPG, пропускаємо
                    if ext in ['.jpg', '.jpeg'] and file_size <= MAX_SIZE:
                        continue

                    # Відкриваємо і зберігаємо як JPG
                    with Image.open(filepath) as img:
                        if img.mode in ("RGBA", "P"):
                            img = img.convert("RGB")
                        
                        new_path = os.path.splitext(filepath)[0] + ".jpg"
                        q = 95
                        img.save(new_path, "JPEG", optimize=True, quality=q)
                        
                        # Стискаємо, якщо треба
                        while os.path.getsize(new_path) / 1024 > MAX_SIZE and q > 10:
                            q -= 5
                            img.save(new_path, "JPEG", optimize=True, quality=q)
                    
                    # Видаляємо старий файл
                    if ext not in ['.jpg', '.jpeg']:
                        time.sleep(0.1)
                        os.remove(filepath)
                        
                    count += 1
                except Exception:
                    continue

    # Показуємо результат
    messagebox.showinfo("Результат", f"Успішно!\nПеретворено та стиснуто файлів: {count}")

if __name__ == "__main__":
    optimize_folder()