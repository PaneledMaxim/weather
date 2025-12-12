"""
Модуль для работы с API open-meteo: геокодирование и получение погоды.
"""
import requests
from datetime import datetime, timezone

BASE_URL = "https://api.open-meteo.com/v1/forecast"
GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"


def geocode_city(city_name: str):
    """Ищет координаты города по имени."""
    params = {"name": city_name, "count": 1, "language": "ru", "format": "json"}
    try:
        resp = requests.get(GEOCODING_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        results = data.get("results")
        if not results:
            return None
        r = results[0]
        return {
            "name": r.get("name"),
            "latitude": r.get("latitude"),
            "longitude": r.get("longitude"),
            "country": r.get("country"),
            "admin1": r.get("admin1")  # Регион
        }
    except requests.RequestException as e:
        print(f"Ошибка геокодирования: {e}")
        return None


def get_weather_by_coordinates(lat: float, lon: float) -> dict:
    """Получает данные о погоде по координатам."""
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": True,
        "hourly": "temperature_2m,relative_humidity_2m,pressure_msl,weather_code",
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum",
        "timezone": "auto",
        "forecast_days": 1
    }
    
    try:
        resp = requests.get(BASE_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        
        # Добавляем время запроса
        data['fetched_at'] = datetime.now(timezone.utc).isoformat()
        
        return data
    except requests.RequestException as e:
        print(f"Ошибка получения погоды: {e}")
        return {"error": f"Ошибка запроса: {e}"}


def get_weather_by_city(city_name: str) -> dict:
    """Получает погоду по названию города."""
    geo = geocode_city(city_name)
    if not geo:
        return {"error": f"Город '{city_name}' не найден."}
    
    try:
        data = get_weather_by_coordinates(geo["latitude"], geo["longitude"])
        if "error" in data:
            return data
        
        return {"meta": geo, "data": data}
    except requests.RequestException as e:
        return {"error": f"Ошибка запроса: {e}"}