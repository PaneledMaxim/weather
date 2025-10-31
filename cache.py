# weather/cache.py
import json
import os
import time
from typing import Optional

CACHE_FILE = "weather_cache.json"
CACHE_TTL = 300  # сек (5 минут)

def _load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def _save_cache(cache: dict):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

