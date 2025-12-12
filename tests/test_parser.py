import unittest
import sys
import os
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.parser import build_parser


class TestParser(unittest.TestCase):
    """Тесты для парсера аргументов командной строки"""
    
    def test_parser_with_city(self):
        """Тест парсера с аргументом --city"""
        parser = build_parser()
        args = parser.parse_args(['--city', 'Moscow'])
        
        self.assertEqual(args.city, 'Moscow')
        self.assertIsNone(args.coords)
    
    def test_parser_with_coords(self):
        """Тест парсера с аргументом --coords"""
        parser = build_parser()
        args = parser.parse_args(['--coords', '55.7558', '37.6173'])
        
        self.assertIsNone(args.city)
        self.assertEqual(args.coords, [55.7558, 37.6173])
    
    def test_parser_mutually_exclusive_group(self):
        """Тест что --city и --coords взаимоисключающие"""
        parser = build_parser()
        
        # Нельзя использовать оба аргумента одновременно
        with self.assertRaises(SystemExit):
            parser.parse_args(['--city', 'Moscow', '--coords', '55.7558', '37.6173'])
    
    def test_parser_no_arguments(self):
        """Тест что хотя бы один аргумент обязателен"""
        parser = build_parser()
        
        with self.assertRaises(SystemExit):
            parser.parse_args([])
    
    def test_parser_help(self):
        """Тест что help работает"""
        parser = build_parser()
        
        with self.assertRaises(SystemExit):  # help вызывает SystemExit
            parser.parse_args(['--help'])
    
    def test_parser_city_with_spaces(self):
        """Тест города с пробелами"""
        parser = build_parser()
        args = parser.parse_args(['--city', 'New York'])
        
        self.assertEqual(args.city, 'New York')
    
    def test_parser_coords_validation(self):
        """Тест что координаты должны быть числами"""
        parser = build_parser()
        
        with self.assertRaises(SystemExit):
            parser.parse_args(['--coords', 'not_a_number', '37.6173'])


if __name__ == '__main__':
    unittest.main()