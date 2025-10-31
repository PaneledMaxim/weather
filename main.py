# main.py
from app.parser import build_parser
from app.commands import weather_by_city, weather_by_coords
from gui import format_weather

def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.city:
        result = weather_by_city(args.city)
    elif args.coords:
        lat, lon = args.coords
        result = weather_by_coords(lat, lon)
    else:
        parser.error("Нужно указать --city или --coords")

    print(format_weather(result))

if __name__ == "__main__":
    main()
