import unittest
from unittest.mock import patch, Mock
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.api import geocode_city, get_weather_by_coordinates, get_weather_by_city
import requests


class TestWeatherAPI(unittest.TestCase):
    """Тесты для модуля работы с API погоды"""
    
    @patch('app.api.requests.get')
    def test_geocode_city_success(self, mock_get):
        """Тест успешного геокодирования города"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [
                {
                    "name": "Moscow",
                    "latitude": 55.7558,
                    "longitude": 37.6173,
                    "country": "Russia"
                }
            ]
        }
        mock_get.return_value = mock_response
        
        result = geocode_city("Moscow")
        
        self.assertEqual(result["name"], "Moscow")
        self.assertEqual(result["latitude"], 55.7558)
        self.assertEqual(result["longitude"], 37.6173)
        self.assertEqual(result["country"], "Russia")
    
    @patch('app.api.requests.get')
    def test_geocode_city_not_found(self, mock_get):
        """Тест геокодирования несуществующего города"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"results": []}
        mock_get.return_value = mock_response
        
        result = geocode_city("UnknownCity")
        
        self.assertIsNone(result)
    
    @patch('app.api.requests.get')
    def test_geocode_city_network_error(self, mock_get):
        """Тест сетевой ошибки при геокодировании"""
        mock_get.side_effect = requests.RequestException("Network error")
        
        with self.assertRaises(requests.RequestException):
            geocode_city("Moscow")
    
    @patch('app.api.requests.get')
    def test_get_weather_by_coordinates_success(self, mock_get):
        """Тест получения погоды по координатам"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "current_weather": {
                "temperature": 15.5,
                "windspeed": 3.2,
                "weathercode": 0
            }
        }
        mock_get.return_value = mock_response
        
        result = get_weather_by_coordinates(55.7558, 37.6173)
        
        self.assertEqual(result["current_weather"]["temperature"], 15.5)
        self.assertEqual(result["current_weather"]["windspeed"], 3.2)
    
    @patch('app.api.requests.get')
    def test_get_weather_by_coordinates_error(self, mock_get):
        """Тест ошибки при получении погоды по координатам"""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.RequestException("API error")
        mock_get.return_value = mock_response
        
        with self.assertRaises(requests.RequestException):
            get_weather_by_coordinates(55.7558, 37.6173)
    
    @patch('app.api.geocode_city')
    @patch('app.api.get_weather_by_coordinates')
    def test_get_weather_by_city_success(self, mock_get_weather, mock_geocode):
        """Тест успешного получения погоды по городу"""
        mock_geocode.return_value = {
            "name": "Moscow",
            "latitude": 55.7558,
            "longitude": 37.6173,
            "country": "Russia"
        }
        mock_get_weather.return_value = {
            "current_weather": {
                "temperature": 15.5,
                "windspeed": 3.2
            }
        }
        
        result = get_weather_by_city("Moscow")
        
        self.assertEqual(result["meta"]["name"], "Moscow")
        self.assertEqual(result["data"]["current_weather"]["temperature"], 15.5)
        mock_geocode.assert_called_once_with("Moscow")
        mock_get_weather.assert_called_once_with(55.7558, 37.6173)
    
    @patch('app.api.geocode_city')
    def test_get_weather_by_city_not_found(self, mock_geocode):
        """Тест получения погоды для несуществующего города"""
        mock_geocode.return_value = None
        
        result = get_weather_by_city("UnknownCity")
        
        self.assertEqual(result["error"], "Город 'UnknownCity' не найден.")
    
    @patch('app.api.geocode_city')
    @patch('app.api.get_weather_by_coordinates')
    def test_get_weather_by_city_api_error(self, mock_get_weather, mock_geocode):
        """Тест ошибки API при получении погоды по городу"""
        mock_geocode.return_value = {
            "latitude": 55.7558,
            "longitude": 37.6173
        }
        mock_get_weather.side_effect = requests.RequestException("API error")
        
        result = get_weather_by_city("Moscow")
        
        self.assertIn("Ошибка запроса:", result["error"])
        self.assertIn("API error", result["error"])


if __name__ == '__main__':
    unittest.main()