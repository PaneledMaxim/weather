import sqlite3
from pathlib import Path
from typing import Any, Optional, List, Dict
import json
from datetime import datetime

DB_PATH = Path(__file__).parent / "weather_data.db"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Инициализировать базу данных"""
    conn = get_conn()
    c = conn.cursor()
    
    # Таблица истории запросов
    c.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT,
            latitude REAL,
            longitude REAL,
            temperature REAL,
            feels_like REAL,
            humidity INTEGER,
            pressure INTEGER,
            windspeed REAL,
            winddirection INTEGER,
            description TEXT,
            weather_code INTEGER,
            is_day INTEGER,
            precipitation REAL,
            cloud_cover INTEGER,
            visibility INTEGER,
            source TEXT,
            api_source TEXT,
            raw_data TEXT,
            requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()


def save_to_history(
    city: Optional[str] = None,
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    temperature: Optional[float] = None,
    feels_like: Optional[float] = None,
    humidity: Optional[int] = None,
    pressure: Optional[int] = None,
    windspeed: Optional[float] = None,
    winddirection: Optional[int] = None,
    description: Optional[str] = None,
    weather_code: Optional[int] = None,
    is_day: Optional[int] = None,
    precipitation: Optional[float] = None,
    cloud_cover: Optional[int] = None,
    visibility: Optional[int] = None,
    source: str = "unknown",
    api_source: str = "",
    raw_data: Optional[Dict] = None
) -> int:
    """Сохранить запись о погоде в историю"""
    conn = get_conn()
    c = conn.cursor()
    
    c.execute("""
        INSERT INTO history (
            city, latitude, longitude, temperature, feels_like, humidity,
            pressure, windspeed, winddirection, description, weather_code,
            is_day, precipitation, cloud_cover, visibility, source, api_source, raw_data
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        city, lat, lon, temperature, feels_like, humidity,
        pressure, windspeed, winddirection, description, weather_code,
        is_day, precipitation, cloud_cover, visibility, source, api_source,
        json.dumps(raw_data) if raw_data else None
    ))
    
    record_id = c.lastrowid
    conn.commit()
    conn.close()
    return record_id


def get_recent_history(limit: int = 10) -> List[Dict]:
    """Получить последние записи из истории"""
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        SELECT * FROM history 
        ORDER BY requested_at DESC 
        LIMIT ?
    """, (limit,))
    
    rows = c.fetchall()
    conn.close()
    
    # Преобразуем raw_data из JSON
    result = []
    for row in rows:
        item = dict(row)
        if item.get('raw_data'):
            try:
                item['raw_data'] = json.loads(item['raw_data'])
            except:
                item['raw_data'] = None
        result.append(item)
    
    return result


def get_history_stats() -> Dict:
    """Получить статистику по истории"""
    conn = get_conn()
    c = conn.cursor()
    
    stats = {}
    
    # Общее количество запросов
    c.execute("SELECT COUNT(*) as total FROM history")
    stats['total_requests'] = c.fetchone()['total']
    
    # Количество уникальных городов
    c.execute("SELECT COUNT(DISTINCT city) as cities FROM history WHERE city IS NOT NULL")
    stats['unique_cities'] = c.fetchone()['cities']
    
    # Средняя температура
    c.execute("SELECT AVG(temperature) as avg_temp FROM history WHERE temperature IS NOT NULL")
    avg_temp = c.fetchone()['avg_temp']
    stats['avg_temperature'] = round(avg_temp, 1) if avg_temp else None
    
    # Минимальная и максимальная температура
    c.execute("SELECT MIN(temperature) as min_temp, MAX(temperature) as max_temp FROM history WHERE temperature IS NOT NULL")
    temps = c.fetchone()
    stats['min_temperature'] = round(temps['min_temp'], 1) if temps['min_temp'] else None
    stats['max_temperature'] = round(temps['max_temp'], 1) if temps['max_temp'] else None
    
    conn.close()
    return stats


def clear_history():
    """Очистить всю историю"""
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM history")
    conn.commit()
    conn.close()