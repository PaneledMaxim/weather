# tests/test_cache.py
import unittest
import os
from pathlib import Path
import sqlite3
from app.cache import get, set

# Путь к тестовой БД (чтобы не трогать настоящую)
TEST_DB_PATH = Path("app/weather_data.db")

class TestCache(unittest.TestCase):
    def setUp(self):
        # Удаляем тестовую БД перед каждым тестом
        if TEST_DB_PATH.exists():
            TEST_DB_PATH.unlink()

        # Принудительно пересоздаём таблицы
        from app.database import init_db
        init_db()

    def tearDown(self):
        # Удаляем после теста
        if TEST_DB_PATH.exists():
            TEST_DB_PATH.unlink()

    def test_cache_set_and_get(self):
        key = "test:key:123"
        data = {"test": "value", "temp": 25.5}

        # Сначала ничего нет
        self.assertIsNone(get(key))

        # Сохраняем
        set(key, data)

        # Достаём — должно быть то же самое
        cached = get(key)
        self.assertEqual(cached, data)

    def test_cache_overwrite(self):
        key = "test:overwrite"
        set(key, {"version": 1})
        set(key, {"version": 2})
        self.assertEqual(get(key)["version"], 2)

    def test_cache_different_keys(self):
        set("key1", {"city": "Moscow"})
        set("key2", {"city": "London"})
        self.assertEqual(get("key1")["city"], "Moscow")
        self.assertEqual(get("key2")["city"], "London")

if __name__ == "__main__":
    unittest.main()