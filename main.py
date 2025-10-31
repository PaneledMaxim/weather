# gui.py
import tkinter as tk
from tkinter import ttk, messagebox
from weather.commands import weather_by_city

def format_weather(result):
    # result может быть либо error, либо структура с meta/data
    r = result.get("result")
    if not r:
        return "Нет данных"
    if isinstance(r, dict) and r.get("error"):
        return f"Ошибка: {r['error']}"
    # Если обёртка с meta и data
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
        lines.append(f"Скорость ветра: {cw.get('windspeed')} km/h")
        lines.append(f"Направление ветра: {cw.get('winddirection')}°")
        lines.append(f"Время: {cw.get('time')}")
    else:
        # Попробуем показать сырые данные
        lines.append("Данных о текущей погоде нет.")
    return "\n".join(lines)

class WeatherApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Погода")
        self.geometry("420x240")
        self.resizable(False, False)
        self.create_widgets()

    def create_widgets(self):
        frm = ttk.Frame(self, padding=12)
        frm.pack(fill=tk.BOTH, expand=True)

        lbl = ttk.Label(frm, text="Город:")
        lbl.grid(column=0, row=0, sticky=tk.W)

        self.city_var = tk.StringVar()
        entry = ttk.Entry(frm, textvariable=self.city_var, width=30)
        entry.grid(column=1, row=0, sticky=tk.W, padx=6)
        entry.bind("<Return>", lambda e: self.get_weather())

        btn = ttk.Button(frm, text="Показать погоду", command=self.get_weather)
        btn.grid(column=2, row=0, sticky=tk.W)

        sep = ttk.Separator(frm, orient='horizontal')
        sep.grid(column=0, row=1, columnspan=3, pady=10, sticky="ew")

        self.status_var = tk.StringVar(value="Введите город и нажмите кнопку")
        status = ttk.Label(frm, textvariable=self.status_var)
        status.grid(column=0, row=2, columnspan=3, sticky=tk.W)

        self.output = tk.Text(frm, height=8, width=50, state=tk.DISABLED, wrap=tk.WORD)
        self.output.grid(column=0, row=3, columnspan=3, pady=8)

    def set_output(self, text):
        self.output.configure(state=tk.NORMAL)
        self.output.delete(1.0, tk.END)
        self.output.insert(tk.END, text)
        self.output.configure(state=tk.DISABLED)

    def get_weather(self):
        city = self.city_var.get().strip()
        if not city:
            messagebox.showwarning("Ошибка", "Введите название города")
            return
        self.status_var.set("Загрузка...")
        self.update_idletasks()
        try:
            result = weather_by_city(city)
            src = result.get("source")
            self.status_var.set(f"Источник: {src}")
            formatted = format_weather(result)
            self.set_output(formatted)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось получить данные: {e}")
            self.status_var.set("Ошибка")

if __name__ == "__main__":
    app = WeatherApp()
    app.mainloop()
