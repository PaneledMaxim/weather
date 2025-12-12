"""
Парсер командной строки для приложения погоды.
"""
import argparse

def build_parser() -> argparse.ArgumentParser:
    """Создаёт и настраивает парсер аргументов CLI.

    Returns:
        argparse.ArgumentParser: Готовый объект парсера.
    """
    parser = argparse.ArgumentParser(description="Weather app (CLI)")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--city", type=str, help="Название города")
    group.add_argument("--coords", nargs=2, type=float, metavar=('LAT','LON'), help="Координаты: широта долгота")
    return parser

if __name__ == "__main__":
    args = build_parser().parse_args()
    print(args)
