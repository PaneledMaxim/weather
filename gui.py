"""Графический интерфейс для получения погоды по городу или координатам."""
import tkinter as tk
from tkinter import ttk, messagebox
from app.commands import weather_by_city, weather_by_coords, get_history, get_statistics
from app.database import init_db, get_recent_history, clear_history
import json
from datetime import datetime


def format_weather(result):
    """Форматирует результат запроса погоды в удобный текст для отображения."""
    r = result.get("result")
    if not r:
        return "Нет данных"
    if isinstance(r, dict) and r.get("error"):
        return f"Ошибка: {r['error']}"
    
    meta = r.get("meta", {})
    data = r.get("data", {})
    cw = data.get("current_weather") if isinstance(data, dict) else None
    
    lines = []
    
    # Заголовок с местом
    if meta:
        name = meta.get("name") or f"{meta.get('latitude')},{meta.get('longitude')}"
        country = meta.get("country")
        title = f"📍 {name}{', ' + country if country else ''}"
        lines.append(title)
        lines.append("─" * 40)
    
    # Текущая погода
    if cw:
        lines.append(f"🌡 Температура: {cw.get('temperature')} °C")
        lines.append(f"💨 Скорость ветра: {cw.get('windspeed')} км/ч")
        lines.append(f"🧭 Направление ветра: {cw.get('winddirection')}°")
        lines.append(f"🕐 Время: {cw.get('time')}")
        
        # Дополнительные данные из hourly если есть
        if "hourly" in data:
            hourly = data["hourly"]
            # Можно добавить дополнительную информацию здесь
            pass
    
    else:
        lines.append("❌ Нет данных о текущей погоде.")
    
    # Время запроса
    lines.append("\n" + "─" * 40)
    lines.append(f"📅 Запрос выполнен: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"🔧 Источник данных: {result.get('source', 'unknown')}")
    
    return "\n".join(lines)


def format_history_entry(entry: dict) -> str:
    """Форматирует одну запись истории"""
    city = entry.get('city') or f"{entry.get('latitude', 0):.2f}, {entry.get('longitude', 0):.2f}"
    temp = f"{entry['temperature']:.1f}°C" if entry.get('temperature') else "—"
    wind = f"{entry['windspeed']} км/ч" if entry.get('windspeed') else "—"
    
    # Форматируем время
    time_str = entry.get('requested_at', '')
    if time_str:
        try:
            dt = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
            time_str = dt.strftime('%H:%M %d.%m')
        except:
            pass
    
    return f"{time_str:15} | {city:20} | {temp:>8} | ветер {wind:>10}"


class WeatherApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Погода")
        self.geometry("700x600")
        
        # Инициализируем БД
        init_db()
        
        # Создаем notebook (вкладки)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Вкладка погоды
        self.weather_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.weather_frame, text="Погода")
        self.create_weather_widgets()
        
        # Вкладка истории
        self.history_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.history_frame, text="История")
        self.create_history_widgets()
        
        # Вкладка статистики
        self.stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.stats_frame, text="Статистика")
        self.create_stats_widgets()
    
    def create_weather_widgets(self):
        """Создает виджеты для вкладки погоды"""
        frm = ttk.Frame(self.weather_frame, padding=15)
        frm.pack(fill=tk.BOTH, expand=True)
        
        # Заголовок
        ttk.Label(frm, text="Запрос погоды", font=('Arial', 14, 'bold')).grid(
            row=0, column=0, columnspan=3, pady=(0, 15))
        
        # Переключатель режима
        self.mode_var = tk.StringVar(value="city")
        mode_frame = ttk.Frame(frm)
        mode_frame.grid(row=1, column=0, columnspan=3, pady=(0, 15), sticky=tk.W)
        
        ttk.Radiobutton(mode_frame, text="По городу", variable=self.mode_var, 
                       value="city", command=self.switch_mode).pack(side=tk.LEFT, padx=(0, 20))
        ttk.Radiobutton(mode_frame, text="По координатам", variable=self.mode_var,
                       value="coords", command=self.switch_mode).pack(side=tk.LEFT)
        
        # Ввод города
        self.city_label = ttk.Label(frm, text="Название города:")
        self.city_entry_var = tk.StringVar()
        self.city_entry = ttk.Entry(frm, textvariable=self.city_entry_var, width=35, font=('Arial', 11))
        self.city_label.grid(row=2, column=0, sticky=tk.W, pady=10)
        self.city_entry.grid(row=2, column=1, sticky=tk.W, padx=10, pady=10)
        
        # Ввод координат
        coord_frame = ttk.Frame(frm)
        
        self.lat_label = ttk.Label(coord_frame, text="Широта:")
        self.lon_label = ttk.Label(coord_frame, text="Долгота:")
        self.lat_var = tk.StringVar()
        self.lon_var = tk.StringVar()
        self.lat_entry = ttk.Entry(coord_frame, textvariable=self.lat_var, width=15, font=('Arial', 11))
        self.lon_entry = ttk.Entry(coord_frame, textvariable=self.lon_var, width=15, font=('Arial', 11))
        
        self.lat_label.grid(row=0, column=0, sticky=tk.W, pady=2)
        self.lat_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        self.lon_label.grid(row=1, column=0, sticky=tk.W, pady=2)
        self.lon_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Кнопка запроса
        ttk.Button(frm, text="Получить погоду", command=self.get_weather).grid(
            row=2, column=2, padx=10, pady=10)
        
        # Статус
        self.status_var = tk.StringVar(value="Готов к работе")
        status_label = ttk.Label(frm, textvariable=self.status_var, foreground="gray")
        status_label.grid(row=3, column=0, columnspan=3, pady=(15, 10), sticky=tk.W)
        
        # Поле вывода с прокруткой
        output_frame = ttk.LabelFrame(frm, text="Результат", padding=10)
        output_frame.grid(row=4, column=0, columnspan=3, sticky="nsew", pady=(10, 0))
        
        # Создаем Text с прокруткой
        self.output_text = tk.Text(output_frame, height=15, wrap=tk.WORD, 
                                 font=('Consolas', 10), bg='#f8f9fa')
        scrollbar = ttk.Scrollbar(output_frame, orient="vertical", command=self.output_text.yview)
        self.output_text.configure(yscrollcommand=scrollbar.set)
        
        self.output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Настройка растягивания
        frm.grid_rowconfigure(4, weight=1)
        frm.grid_columnconfigure(1, weight=1)
        
        # Изначально скрываем координаты
        coord_frame.grid_remove()
        
        # Привязываем Enter к запросу погоды
        self.city_entry.bind("<Return>", lambda e: self.get_weather())
        self.lat_entry.bind("<Return>", lambda e: self.get_weather())
        self.lon_entry.bind("<Return>", lambda e: self.get_weather())
    
    def switch_mode(self):
        """Переключение между режимами ввода"""
        if self.mode_var.get() == "city":
            # Показываем город
            self.city_label.grid()
            self.city_entry.grid()
            # Скрываем координаты
            self.lat_label.master.grid_remove()
        else:
            # Скрываем город
            self.city_label.grid_remove()
            self.city_entry.grid_remove()
            # Показываем координаты
            self.lat_label.master.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=10)
    
    def create_history_widgets(self):
        """Создает виджеты для вкладки истории"""
        frm = ttk.Frame(self.history_frame, padding=15)
        frm.pack(fill=tk.BOTH, expand=True)
        
        # Панель управления
        control_frame = ttk.Frame(frm)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(control_frame, text="Количество записей:").pack(side=tk.LEFT, padx=(0, 5))
        self.history_limit_var = tk.IntVar(value=20)
        ttk.Spinbox(control_frame, from_=5, to=100, textvariable=self.history_limit_var,
                   width=8, command=self.refresh_history).pack(side=tk.LEFT, padx=(0, 15))
        
        ttk.Button(control_frame, text="Обновить", command=self.refresh_history).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Очистить историю", command=self.clear_history).pack(side=tk.LEFT, padx=5)
        
        # Текст с историей
        history_frame = ttk.LabelFrame(frm, text="История запросов", padding=10)
        history_frame.pack(fill=tk.BOTH, expand=True)
        
        self.history_text = tk.Text(history_frame, height=20, wrap=tk.WORD, 
                                  font=('Consolas', 9), bg='#f8f9fa')
        scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=self.history_text.yview)
        self.history_text.configure(yscrollcommand=scrollbar.set)
        
        self.history_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Загружаем историю при открытии
        self.refresh_history()
    
    def create_stats_widgets(self):
        """Создает виджеты для вкладки статистики"""
        frm = ttk.Frame(self.stats_frame, padding=20)
        frm.pack(fill=tk.BOTH, expand=True)
        
        # Статистика
        stats_frame = ttk.LabelFrame(frm, text="Статистика", padding=15)
        stats_frame.pack(fill=tk.BOTH, expand=True)
        
        self.stats_text = tk.Text(stats_frame, height=15, wrap=tk.WORD, 
                                font=('Consolas', 11), bg='#f8f9fa')
        scrollbar = ttk.Scrollbar(stats_frame, orient="vertical", command=self.stats_text.yview)
        self.stats_text.configure(yscrollcommand=scrollbar.set)
        
        self.stats_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        ttk.Button(frm, text="Обновить статистику", command=self.refresh_stats).pack(pady=10)
        
        self.refresh_stats()
    
    def get_weather(self):
        """Получить погоду"""
        mode = self.mode_var.get()
        self.status_var.set("Загрузка...")
        self.output_text.delete(1.0, tk.END)
        
        try:
            if mode == "city":
                city = self.city_entry_var.get().strip()
                if not city:
                    messagebox.showwarning("Ошибка", "Введите название города")
                    self.status_var.set("Ошибка: введите город")
                    return
                result = weather_by_city(city)
            else:
                try:
                    lat = float(self.lat_var.get())
                    lon = float(self.lon_var.get())
                except ValueError:
                    messagebox.showwarning("Ошибка", "Введите корректные числа для координат")
                    self.status_var.set("Ошибка: некорректные координаты")
                    return
                result = weather_by_coords(lat, lon)
            
            # Форматируем вывод
            formatted = format_weather(result)
            self.output_text.insert(tk.END, formatted)
            self.status_var.set(f"Готово. Источник: {result.get('source', 'unknown')}")
            
            # Обновляем историю и статистику
            self.refresh_history()
            self.refresh_stats()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось получить данные: {e}")
            self.status_var.set("Ошибка")
            self.output_text.insert(tk.END, f"Ошибка: {str(e)}")
    
    def refresh_history(self):
        """Обновить историю"""
        limit = self.history_limit_var.get()
        history = get_history(limit)
        
        self.history_text.delete(1.0, tk.END)
        
        if not history:
            self.history_text.insert(tk.END, "История запросов пуста.\n")
            return
        
        # Заголовок
        self.history_text.insert(tk.END, "Последние запросы погоды:\n")
        self.history_text.insert(tk.END, "=" * 70 + "\n\n")
        
        # Записи
        for i, entry in enumerate(history, 1):
            formatted = format_history_entry(entry)
            self.history_text.insert(tk.END, f"{i:2}. {formatted}\n")
    
    def refresh_stats(self):
        """Обновить статистику"""
        stats = get_statistics()
        
        self.stats_text.delete(1.0, tk.END)
        
        text = "📊 Статистика запросов погоды\n"
        text += "=" * 50 + "\n\n"
        
        text += f"📈 Всего запросов: {stats.get('total_requests', 0)}\n"
        text += f"🏙️ Уникальных городов: {stats.get('unique_cities', 0)}\n\n"
        
        if stats.get('avg_temperature'):
            text += f"🌡️ Средняя температура: {stats['avg_temperature']}°C\n"
            text += f"❄️ Минимальная температура: {stats['min_temperature']}°C\n"
            text += f"🔥 Максимальная температура: {stats['max_temperature']}°C\n"
        else:
            text += "🌡️ Нет данных о температуре\n"
        
        text += "\n" + "=" * 50 + "\n"
        text += f"📅 Обновлено: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        self.stats_text.insert(tk.END, text)
    
    def clear_history(self):
        """Очистить историю"""
        if messagebox.askyesno("Подтверждение", 
                              "Вы уверены, что хотите очистить всю историю?\nЭто действие нельзя отменить."):
            clear_history()
            self.refresh_history()
            self.refresh_stats()
            messagebox.showinfo("Успех", "История успешно очищена")


if __name__ == "__main__":
    app = WeatherApp()
    app.mainloop()