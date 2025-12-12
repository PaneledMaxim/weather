#!/usr/bin/env python3
"""
Скрипт для сброса базы данных
"""
import os
from pathlib import Path
from app.database import init_db

if __name__ == "__main__":
    # Удаляем старую БД если существует
    db_path = Path("app/weather_data.db")
    if db_path.exists():
        os.remove(db_path)
        print("✅ Старая БД удалена")
    
    # Создаем новую
    init_db()
    print("✅ Новая БД создана с правильной структурой")
    print("\nСтруктура таблицы history:")
    print("  - id (INTEGER PRIMARY KEY)")
    print("  - city (TEXT)")
    print("  - latitude (REAL)")
    print("  - longitude (REAL)")
    print("  - temperature (REAL)")
    print("  - windspeed (REAL)")
    print("  - winddirection (INTEGER)")
    print("  - source (TEXT)")
    print("  - api_source (TEXT)")
    print("  - raw_data (TEXT)")
    print("  - requested_at (TIMESTAMP)")