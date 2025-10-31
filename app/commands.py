# weather/commands.py
from .api import get_weather_by_city, get_weather_by_coordinates
from .cache import get, set

def weather_by_city(city: str):
    key = f"city:{city.strip().lower()}"
    cached = get(key)
    if cached:
        return {"source": "cache", "result": cached}
    result = get_weather_by_city(city)
    set(key, result)
    return {"source": "api", "result": result}

def weather_by_coords(lat: float, lon: float):
    key = f"coords:{lat},{lon}"
    cached = get(key)
    if cached:
        return {"source": "cache", "result": cached}
    result = get_weather_by_coordinates(lat, lon)
    wrapped = {"meta": {"latitude": lat, "longitude": lon}, "data": result}
    set(key, wrapped)
    return {"source": "api", "result": wrapped}
