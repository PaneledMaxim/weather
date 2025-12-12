"""
Модуль для работы с временным кэшем в памяти
"""
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from .database import save_to_history

# Простой кэш в памяти
_memory_cache = {}
_CACHE_TTL = timedelta(minutes=30)


def get_from_cache(key: str) -> Optional[Dict]:
    """Получить данные из кэша памяти"""
    if key in _memory_cache:
        data, timestamp = _memory_cache[key]
        if datetime.now() - timestamp < _CACHE_TTL:
            return data
        else:
            del _memory_cache[key]  # Удалить просроченный кэш
    return None


def set_to_cache(key: str, data: Dict) -> None:
    """Сохранить данные в кэш памяти"""
    _memory_cache[key] = (data, datetime.now())


def save_weather_to_history(weather_data: Dict, source: str = "api", city: str = None, lat: float = None, lon: float = None) -> int:
    """
    Сохранить данные о погоде в историю
    
    Args:
        weather_data: Данные о погоде
        source: Источник данных ('api' или 'cache')
        city: Название города (опционально)
        lat: Широта (опционально)
        lon: Долгота (опционально)
    
    Returns:
        ID сохраненной записи
    """
    try:
        # Извлекаем данные из структуры API
        result = weather_data.get("result", weather_data)
        
        # Определяем метаданные
        meta = result.get("meta", {})
        api_data = result.get("data", result)
        
        # Извлекаем текущую погоду
        current_weather = api_data.get("current_weather", {})
        
        # Сохраняем в БД
        record_id = save_to_history(
            city=city or meta.get("name"),
            lat=lat or meta.get("latitude") or api_data.get("latitude"),
            lon=lon or meta.get("longitude") or api_data.get("longitude"),
            temperature=current_weather.get("temperature"),
            windspeed=current_weather.get("windspeed"),
            winddirection=current_weather.get("winddirection"),
            source=source,
            api_source="open-meteo",
            raw_data=weather_data
        )
        
        return record_id
        
    except Exception as e:
        print(f"Ошибка при сохранении в историю: {e}")
        return -1