# weather/parser.py
import argparse

def build_parser():
    parser = argparse.ArgumentParser(description="Weather app (CLI)")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--city", type=str, help="Название города")
    group.add_argument("--coords", nargs=2, type=float, metavar=('LAT','LON'), help="Координаты: широта долгота")
    return parser
