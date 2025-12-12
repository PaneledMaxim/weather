"""
Команды верхнего уровня для получения данных о погоде.
"""
from .api import get_weather_by_city, get_weather_by_coordinates
from .cache import get_from_cache, set_to_cache, save_weather_to_history


def weather_by_city(city: str) -> dict:
    """Возвращает погоду по городу с использованием кэша."""
    key = f"city:{city.strip().lower()}"
    
    # Проверяем кэш в памяти
    cached = get_from_cache(key)
    if cached:
        # Сохраняем в историю (из кэша)
        save_weather_to_history(cached, source="cache", city=city)
        return {"source": "cache", "result": cached}
    
    # Получаем из API
    result = get_weather_by_city(city)
    
    # Сохраняем в кэш
    set_to_cache(key, result)
    
    # Сохраняем в историю (из API)
    if "error" not in result:
        save_weather_to_history({"result": result}, source="api", city=city)
    
    return {"source": "api", "result": result}


def weather_by_coords(lat: float, lon: float) -> dict:
    """Возвращает погоду по координатам с использованием кэша."""
    key = f"coords:{lat},{lon}"
    
    # Проверяем кэш в памяти
    cached = get_from_cache(key)
    if cached:
        # Сохраняем в историю (из кэша)
        save_weather_to_history(cached, source="cache", lat=lat, lon=lon)
        return {"source": "cache", "result": cached}
    
    # Получаем из API
    result = get_weather_by_coordinates(lat, lon)
    
    # Оборачиваем в стандартный формат
    wrapped = {"meta": {"latitude": lat, "longitude": lon}, "data": result}
    
    # Сохраняем в кэш
    set_to_cache(key, wrapped)
    
    # Сохраняем в историю (из API)
    save_weather_to_history({"result": wrapped}, source="api", lat=lat, lon=lon)
    
    return {"source": "api", "result": wrapped}


def get_history(limit: int = 10):
    """Получить историю запросов"""
    from .database import get_recent_history
    return get_recent_history(limit)


def get_statistics():
    """Получить статистику по истории"""
    from .database import get_history_stats
    return get_history_stats()