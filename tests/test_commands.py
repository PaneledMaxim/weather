# tests/test_commands.py
import unittest
from unittest.mock import patch

from app.database import init_db
from app.commands import weather_by_city, weather_by_coords


class TestCommands(unittest.TestCase):

    def setUp(self):
        # ← Гарантируем, что таблицы существуют
        init_db()
        # ← ОЧИЩАЕМ кэш перед каждым тестом — это главное!
        from app.database import get_conn
        conn = get_conn()
        conn.execute("DELETE FROM cache")
        conn.commit()
        conn.close()

    @patch('app.api.get_weather_by_city')
    def test_weather_by_city_from_api(self, mock_get):
        # open‑meteo возвращает русское название
        mock_get.return_value = {
            "meta": {"name": "Москва", "latitude": 55.75, "longitude": 37.62},
            "data": {"current_weather": {"temperature": 15.0, "windspeed": 5.0, "winddirection": 180}}
        }
        result = weather_by_city("Moscow")
        self.assertEqual(result["source"], "api")
        self.assertEqual(result["result"]["meta"]["name"], "Москва")   # ← теперь ожидается русский

    @patch('app.api.get_weather_by_city')
    def test_weather_by_city_from_cache(self, mock_get):
        mock_get.return_value = {
            "meta": {"name": "Москва"},
            "data": {"current_weather": {"temperature": 20.0, "windspeed": 3.0, "winddirection": 90}}
        }
        weather_by_city("Moscow")          # первый → из API
        result = weather_by_city("Moscow") # второй → из кэша
        self.assertEqual(result["source"], "cache")

    @patch('app.api.get_weather_by_city')
    def test_weather_by_city_strip_lowercase(self, mock_get):
        mock_get.return_value = {
            "meta": {"name": "Москва", "latitude": 55.75, "longitude": 37.62},
            "data": {"current_weather": {"temperature": 15.0, "windspeed": 5.0, "winddirection": 180}}
        }

        result1 = weather_by_city("  Moscow  ")
        result2 = weather_by_city("moscow")
        result3 = weather_by_city("MOSCOW")

        self.assertEqual(result1["source"], "api")    # первый — из API
        self.assertEqual(result2["source"], "cache")  # остальные — из кэша
        self.assertEqual(result3["source"], "cache")

    @patch('app.api.get_weather_by_coordinates')
    def test_weather_by_coords_from_api(self, mock_get):
        mock_get.return_value = {"current_weather": {"temperature": 10.0}}
        result = weather_by_coords(55.75, 37.62)
        self.assertEqual(result["source"], "api")

    @patch('app.api.get_weather_by_coordinates')
    def test_weather_by_coords_from_cache(self, mock_get):
        mock_get.return_value = {"current_weather": {"temperature": 12.0}}
        weather_by_coords(55.75, 37.62)
        result = weather_by_coords(55.75, 37.62)
        self.assertEqual(result["source"], "cache")