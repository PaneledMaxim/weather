# weather/api.py
import requests

BASE_URL = "https://api.open-meteo.com/v1/forecast"
GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"

def geocode_city(city_name):
    params = {"name": city_name, "count": 1, "language": "ru"}
    resp = requests.get(GEOCODING_URL, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    results = data.get("results")
    if not results:
        return None
    r = results[0]
    return {"name": r.get("name"), "latitude": r.get("latitude"), "longitude": r.get("longitude"), "country": r.get("country")}

def get_weather_by_coordinates(lat, lon):
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": True,
        "timezone": "auto"
    }
    resp = requests.get(BASE_URL, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()

def get_weather_by_city(city_name):
    geo = geocode_city(city_name)
    if not geo:
        return {"error": f"Город '{city_name}' не найден."}
    try:
        data = get_weather_by_coordinates(geo["latitude"], geo["longitude"])
        return {"meta": geo, "data": data}
    except requests.RequestException as e:
        return {"error": f"Ошибка запроса: {e}"}
