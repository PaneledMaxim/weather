"""Точка входа для запуска консольного приложения погоды.

Позволяет получить текущую погоду по названию города или координатам.
Использует функции из app.commands и форматирование из gui.
"""
from app.parser import build_parser
from app.commands import weather_by_city, weather_by_coords, get_history
from gui import format_weather, format_history
from app.database import init_db

def main():
    """Парсит аргументы командной строки и выводит погоду или историю.
    
    Аргументы командной строки:
        --city CITY: название города
        --coords LAT LON: широта и долгота  
        --history: показать историю запросов
        --stats: показать статистику
        --limit N: количество записей истории
        
    Returns:
        None: выводит результат в консоль.
    """
    init_db()
    parser = build_parser()
    args = parser.parse_args()

    if args.city:
        result = weather_by_city(args.city)
        print(format_weather(result))
        
    elif args.coords:
        lat, lon = args.coords
        result = weather_by_coords(lat, lon)
        print(format_weather(result))
        
    elif args.history:
        history = get_history(args.limit)
        print(format_history(history))
        
    elif args.stats:
        history = get_history(100)  # Больше записей для статистики
        print(format_history(history, stats=True))
        
    else:
        parser.error("Нужно указать --city, --coords, --history или --stats")

if __name__ == "__main__":
    main()