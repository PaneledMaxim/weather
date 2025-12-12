# app/cache.py
from .database import cache_get, cache_set, add_to_history, init_db

init_db()

def get(key: str):
    return cache_get(key)

def set(key: str, data: dict) -> None:
    cache_set(key, data)
    
    # === Записываем в историю только при реальном запросе к API ===
    if data.get("source") == "api":
        result = data["result"]
        cw = None
        city = None
        lat = lon = None
        
        if "meta" in result:
            meta = result["meta"]
            city = meta.get("name")
            lat = meta.get("latitude")
            lon = meta.get("longitude")
            cw = result["data"]["current_weather"]
        elif "data" in result:
            cw = result["data"]["current_weather"]
            # по координатам — город не знаем
        else:
            cw = result.get("current_weather")
        
        if cw:
            add_to_history(
                city=city,
                lat=lat,
                lon=lon,
                temperature=cw["temperature"],
                windspeed=cw["windspeed"],
                winddirection=cw["winddirection"],
                source="api"
            )