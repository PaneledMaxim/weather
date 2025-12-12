# app/database.py
import sqlite3
from pathlib import Path
from typing import Any, Optional, List, Dict
import json

DB_PATH = Path(__file__).parent / "weather_data.db"

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS cache (
            key TEXT PRIMARY KEY,
            data TEXT NOT NULL,
            fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT,
            latitude REAL,
            longitude REAL,
            temperature REAL,
            windspeed REAL,
            winddirection INTEGER,
            source TEXT,
            requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def cache_get(key: str) -> Optional[Any]:
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT data FROM cache WHERE key = ?", (key,))
    row = c.fetchone()
    conn.close()
    return json.loads(row["data"]) if row else None

def cache_set(key: str, data: Any) -> None:
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        INSERT INTO cache (key, data) VALUES (?, ?)
        ON CONFLICT(key) DO UPDATE SET data=excluded.data, fetched_at=CURRENT_TIMESTAMP
    """, (key, json.dumps(data)))
    conn.commit()
    conn.close()

def add_to_history(city: Optional[str], lat: Optional[float], lon: Optional[float],
                   temperature: float, windspeed: float, winddirection: int, source: str) -> None:
    conn = get_conn
    c = conn.cursor()
    c.execute("""
        INSERT INTO history (city, latitude, longitude, temperature, windspeed, winddirection, source)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (city, lat, lon, temperature, windspeed, winddirection, source))
    conn.commit()
    conn.close()

def get_history(limit: int = 10) -> List[Dict]:
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM history ORDER BY requested_at DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]