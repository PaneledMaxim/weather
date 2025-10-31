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

def get(key: str) -> Optional[dict]:
    cache = _load_cache()
    entry = cache.get(key)
    if not entry:
        return None
    if time.time() - entry.get("timestamp", 0) > CACHE_TTL:
        # устарело
        cache.pop(key, None)
        _save_cache(cache)
        return None
    return entry.get("data")

def set(key: str, data: dict):
    cache = _load_cache()
    cache[key] = {"data": data, "timestamp": time.time()}
    _save_cache(cache)
