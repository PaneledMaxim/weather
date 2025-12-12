# show_db.py — просто запусти: py show_db.py
import sqlite3
from pathlib import Path

db_path = Path("app/weather_data.db")
if not db_path.exists():
    print("База не найдена! Сделай пару запросов погоды сначала.")
    exit()

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

print("ИСТОРИЯ ПОГОДЫ (последние 15 запросов)".center(90, "="))
cur.execute("SELECT * FROM history ORDER BY requested_at DESC LIMIT 15")
for row in cur.fetchall():
    city = row["city"] or f"{row['latitude']}, {row['longitude']}"
    temp = f"{row['temperature']:.1f}°C" if row["temperature"] else "—"
    wind = f"{row['windspeed']} км/ч" if row["windspeed"] else "—"
    time = row["requested_at"][:19]
    print(f"{time}  |  {city:25}  |  {temp:>6}  |  ветер {wind:>8}  |  {row['source']}")

print("\nКЭШ (последние 10 записей)".center(90, "-"))
cur.execute("SELECT key, fetched_at FROM cache ORDER BY fetched_at DESC LIMIT 10")
for row in cur.fetchall():
    print(f"{row['fetched_at'][:19]}  ←  {row['key']}")



conn.close()
print("\nГотово!")
