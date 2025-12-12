"""Графический интерфейс для получения погоды по городу или координатам.

Использует функции weather_by_city и weather_by_coords из app.commands.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from app.commands import weather_by_city, weather_by_coords
from app.database import init_db


def format_weather(result):
    """Форматирует результат запроса погоды в удобный текст для отображения.

    Args:
        result (dict): Словарь с ключом "result" от API или кеша.

    Returns:
        str: Отформатированная строка с погодой или сообщением об ошибке.
    """
    r = result.get("result")
    if not r:
        return "Нет данных"
    if isinstance(r, dict) and r.get("error"):
        return f"Ошибка: {r['error']}"
    meta = r.get("meta", {})
    data = r.get("data", {})
    cw = data.get("current_weather") if isinstance(data, dict) else None
    lines = []
    if meta:
        name = meta.get("name") or f"{meta.get('latitude')},{meta.get('longitude')}"
        country = meta.get("country")
        title = f"{name}{', ' + country if country else ''}"
        lines.append(title)
    if cw:
        lines.append(f"Температура: {cw.get('temperature')} °C")
        lines.append(f"Скорость ветра: {cw.get('windspeed')} км/ч")
        lines.append(f"Направление ветра: {cw.get('winddirection')}°")
        lines.append(f"Время: {cw.get('time')}")
    else:
        lines.append("Нет данных о текущей погоде.")
    return "\n".join(lines)


class WeatherApp(tk.Tk):
    """Главное окно приложения Tkinter для отображения погоды.

    Атрибуты:
        mode_var (tk.StringVar): Режим ввода ('city' или 'coords').
        city_entry_var (tk.StringVar): Ввод названия города.
        lat_var (tk.StringVar): Ввод широты.
        lon_var (tk.StringVar): Ввод долготы.
        status_var (tk.StringVar): Статус приложения.
        output (tk.Text): Виджет для вывода результата.
    """
    def __init__(self):
        super().__init__()
        self.title("Погода")
        self.geometry("460x280")
        self.resizable(False, False)
        self.create_widgets()

    def create_widgets(self):
        """Создаёт и размещает все виджеты интерфейса."""
        frm = ttk.Frame(self, padding=12)
        frm.pack(fill=tk.BOTH, expand=True)

        # --- Переключатель режима ---
        self.mode_var = tk.StringVar(value="city")
        rb_city = ttk.Radiobutton(frm, text="По городу", variable=self.mode_var, value="city", command=self.switch_mode)
        rb_coords = ttk.Radiobutton(frm, text="По координатам", variable=self.mode_var, value="coords", command=self.switch_mode)
        rb_city.grid(column=0, row=0, sticky=tk.W)
        rb_coords.grid(column=1, row=0, sticky=tk.W, padx=8)

        # --- Ввод для города ---
        self.city_label = ttk.Label(frm, text="Город:")
        self.city_entry_var = tk.StringVar()
        self.city_entry = ttk.Entry(frm, textvariable=self.city_entry_var, width=30)

        self.city_label.grid(column=0, row=1, sticky=tk.W, pady=4)
        self.city_entry.grid(column=1, row=1, sticky=tk.W, padx=6)
        self.city_entry.bind("<Return>", lambda e: self.get_weather())

        # --- Ввод для координат ---
        self.lat_label = ttk.Label(frm, text="Широта:")
        self.lon_label = ttk.Label(frm, text="Долгота:")
        self.lat_var = tk.StringVar()
        self.lon_var = tk.StringVar()
        self.lat_entry = ttk.Entry(frm, textvariable=self.lat_var, width=10)
        self.lon_entry = ttk.Entry(frm, textvariable=self.lon_var, width=10)

        # Изначально скрываем поля координат
        self.lat_label.grid_forget()
        self.lon_label.grid_forget()
        self.lat_entry.grid_forget()
        self.lon_entry.grid_forget()

        # --- Кнопка ---
        btn = ttk.Button(frm, text="Показать погоду", command=self.get_weather)
        btn.grid(column=2, row=1, sticky=tk.W, padx=4)

        sep = ttk.Separator(frm, orient='horizontal')
        sep.grid(column=0, row=2, columnspan=3, pady=10, sticky="ew")

        self.status_var = tk.StringVar(value="Выберите режим и введите данные")
        status = ttk.Label(frm, textvariable=self.status_var)
        status.grid(column=0, row=3, columnspan=3, sticky=tk.W)

        self.output = tk.Text(frm, height=8, width=55, state=tk.DISABLED, wrap=tk.WORD)
        self.output.grid(column=0, row=4, columnspan=3, pady=8)

    def switch_mode(self):
        """Переключение между режимами ввода"""
        mode = self.mode_var.get()
        if mode == "city":
            # показать поля города, скрыть координаты
            self.city_label.grid(column=0, row=1, sticky=tk.W, pady=4)
            self.city_entry.grid(column=1, row=1, sticky=tk.W, padx=6)
            self.lat_label.grid_forget()
            self.lon_label.grid_forget()
            self.lat_entry.grid_forget()
            self.lon_entry.grid_forget()
        else:
            # показать координаты, скрыть город
            self.city_label.grid_forget()
            self.city_entry.grid_forget()
            self.lat_label.grid(column=0, row=1, sticky=tk.W)
            self.lat_entry.grid(column=1, row=1, sticky=tk.W, padx=4)
            self.lon_label.grid(column=0, row=2, sticky=tk.W)
            self.lon_entry.grid(column=1, row=2, sticky=tk.W, padx=4)

    def set_output(self, text):
        """Выводит текст в виджет Text.

        Args:
            text (str): Текст для отображения.
        """
        self.output.configure(state=tk.NORMAL)
        self.output.delete(1.0, tk.END)
        self.output.insert(tk.END, text)
        self.output.configure(state=tk.DISABLED)

    def get_weather(self):
        """Получает данные погоды и выводит их в интерфейс.

        Обрабатывает ошибки ввода и ошибки запроса.
        """
        mode = self.mode_var.get()
        self.status_var.set("Загрузка...")
        self.update_idletasks()
        try:
            if mode == "city":
                city = self.city_entry_var.get().strip()
                if not city:
                    messagebox.showwarning("Ошибка", "Введите название города")
                    return
                result = weather_by_city(city)
            else:
                try:
                    lat = float(self.lat_var.get())
                    lon = float(self.lon_var.get())
                except ValueError:
                    messagebox.showwarning("Ошибка", "Введите корректные числа для широты и долготы")
                    return
                result = weather_by_coords(lat, lon)

            src = result.get("source")
            self.status_var.set(f"Источник: {src}")
            formatted = format_weather(result)
            self.set_output(formatted)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось получить данные: {e}")
            self.status_var.set("Ошибка")

    def format_history(entries: list, stats: bool = False) -> str:
        if not entries:
            return "История запросов пуста.\n"
        
        lines = ["Последние запросы погоды:", "-" * 60]
        
        for e in entries:
            city = e['city'] or f"{e['latitude']}, {e['longitude']}"
            temp = f"{e['temperature']:.1f}°C" if e['temperature'] is not None else "—"
            wind = f"{e['windspeed']} км/ч" if e['windspeed'] else "—"
            time = e['requested_at'][:19]
            lines.append(f"{time} | {city:20} | {temp:>6} | ветер {wind}")
        
        if stats:
            temps = [e['temperature'] for e in entries if e['temperature']]
            if temps:
                lines.append("-" * 60)
                lines.append(f"Статистика: средняя {sum(temps)/len(temps):.1f}°C, "
                            f"мин {min(temps):.1f}°C, макс {max(temps):.1f}°C")
        
        return "\n".join(lines)


if __name__ == "__main__":
    init_db()
    app = WeatherApp()
    app.mainloop()
