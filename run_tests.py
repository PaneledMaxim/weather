#!/usr/bin/env python3
"""
Скрипт для запуска всех тестов приложения погоды
"""
import unittest
import sys
import os


def run_all_tests():
    """Запуск всех тестов и возврат результата"""
    # Добавляем текущую директорию в путь для импортов
    sys.path.insert(0, os.path.abspath('.'))
    
    print("Запуск тестов приложения погоды...")
    print("=" * 50)
    
    # Находим и запускаем все тесты
    loader = unittest.TestLoader()
    start_dir = 'tests'
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # Запускаем тесты с детальным выводом
    runner = unittest.TextTestRunner(verbosity=2, failfast=False)
    result = runner.run(suite)
    
    print("=" * 50)
    if result.wasSuccessful():
        print("✅ Все тесты прошли успешно!")
        return True
    else:
        print("❌ Некоторые тесты не прошли")
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)