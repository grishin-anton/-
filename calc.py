import tkinter as tk
from tkinter import messagebox, ttk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class CalculatorApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Многофункциональный Калькулятор")
        self.master.geometry("500x400")  # Увеличенный размер окна
        self.master.resizable(False, False)

        # Основной стиль
        style = ttk.Style(self.master)
        style.theme_use('clam')
        style.configure('TButton', font=('Segoe UI', 11))
        style.configure('TLabel', font=('Segoe UI', 12))
        style.configure('Header.TLabel', font=('Segoe UI', 14, 'bold'))

        # Режим работы: combobox для выбора
        modes_frame = ttk.Frame(self.master)
        modes_frame.pack(pady=10, padx=10, fill='x')

        ttk.Label(modes_frame, text="Выберите режим работы:", style='Header.TLabel').pack(anchor='w')

        self.mode_var = tk.StringVar(value="Калькулятор")
        self.mode_cb = ttk.Combobox(
            modes_frame,
            textvariable=self.mode_var,
            values=["Калькулятор", "Решение уравнений", "Построение графика"],
            state="readonly",
            font=('Segoe UI', 11)
        )
        self.mode_cb.pack(fill='x', pady=5)
        self.mode_cb.bind("<<ComboboxSelected>>", self.mode_changed)

        # Ввод данных
        input_frame = ttk.Frame(self.master)
        input_frame.pack(pady=10, padx=10, fill='x')

        ttk.Label(input_frame, text="Введите выражение:", style='TLabel').pack(anchor='w')

        self.input_entry = ttk.Entry(input_frame, font=('Segoe UI', 13))
        self.input_entry.pack(fill='x', pady=5)

        # Кнопки действий
        btns_frame = ttk.Frame(self.master)
        btns_frame.pack(pady=10, padx=10, fill='x')

        self.calc_button = ttk.Button(btns_frame, text="Вычислить / Решить", command=self.calculate)
        self.calc_button.pack(side='left', expand=True, fill='x', padx=(0, 5))

        self.graph_button = ttk.Button(btns_frame, text="Построить график", command=self.plot_graph)
        self.graph_button.pack(side='left', expand=True, fill='x', padx=(5, 0))

        # Результат
        output_frame = ttk.Frame(self.master)
        output_frame.pack(pady=10, padx=10, fill='both', expand=True)

        ttk.Label(output_frame, text="Результат:", style='Header.TLabel').pack(anchor='w')

        self.result_text = tk.Text(output_frame, height=7, font=('Segoe UI', 11), state='disabled', wrap='word')
        self.result_text.pack(fill='both', expand=True)

        # Изначально скрываем кнопку построения графика (не калькулятор/уравнения)
        self.graph_button.pack_forget()

        self.update_placeholder()

        self.graph_window = None  # Ссылка на окно графика, если открыто

    def mode_changed(self, event=None):
        mode = self.mode_var.get()
        self.result_text.config(state='normal')
        self.result_text.delete('1.0', tk.END)
        self.result_text.config(state='disabled')
        if mode == "Калькулятор":
            self.calc_button.config(text="Вычислить")
            self.graph_button.pack_forget()
            self.close_graph_window()
        elif mode == "Решение уравнений":
            self.calc_button.config(text="Решить")
            self.graph_button.pack_forget()
            self.close_graph_window()
        else:  # Построение графика
            self.calc_button.config(text="Вычислить / Решить")
            self.graph_button.pack(side='left', expand=True, fill='x', padx=(5, 0))
        self.update_placeholder()

    def update_placeholder(self):
        mode = self.mode_var.get()
        self.input_entry.delete(0, tk.END)
        if mode == "Калькулятор":
            self.input_entry.insert(0, "3 * (2 + 1)")
        elif mode == "Решение уравнений":
            self.input_entry.insert(0, "2x + 3 = 7")
        else:
            self.input_entry.insert(0, "np.sin(x)")

    def append_result(self, text):
        self.result_text.config(state='normal')
        self.result_text.insert(tk.END, text + "\n")
        self.result_text.config(state='disabled')
        self.result_text.see(tk.END)

    def calculate(self):
        input_text = self.input_entry.get()
        mode = self.mode_var.get()
        try:
            if mode == "Калькулятор":
                result = eval(input_text, {"__builtins__": None}, {"np": np})
                self.result_text.config(state='normal')
                self.result_text.delete('1.0', tk.END)
                self.append_result(f"Результат: {result}")
            elif mode == "Решение уравнений":
                self.result_text.config(state='normal')
                self.result_text.delete('1.0', tk.END)
                solution = self.solve_equation(input_text)
                self.append_result(f"{solution}")
            else:
                self.result_text.config(state='normal')
                self.result_text.delete('1.0', tk.END)
                self.append_result("Для построения графика используйте кнопку 'Построить график'")
        except Exception as e:
            messagebox.showerror("Ошибка", "Неверный ввод. Пожалуйста, попробуйте снова.")
            self.append_result(f"Ошибка: {str(e)}")

    def solve_equation(self, equation):
        try:
            eq = equation.replace(" ", "")
            if "=" not in eq:
                return "Уравнение должно содержать знак '='."
            left, right = eq.split("=")
            right_val = float(right)

            if "x" in left:
                left = left.replace("+", "")
                terms = []
                i = 0
                while i < len(left):
                    if left[i] in "+-":
                        terms.append(left[i])
                        i += 1
                    else:
                        num = ""
                        while i < len(left) and (left[i].isdigit() or left[i] == '.'):
                            num += left[i]
                            i += 1
                        if i < len(left) and left[i] == 'x':
                            num += 'x'
                            i += 1
                        terms.append(num)
                a = 0
                b = 0
                for term in terms:
                    if 'x' in term:
                        coeff = term.replace('x', '')
                        if coeff in ['', '+']:
                            coeff = 1
                        elif coeff == '-':
                            coeff = -1
                        else:
                            coeff = float(coeff)
                        a += coeff
                    else:
                        if term in ['+', '-']:
                            continue
                        b += float(term)
                x = (right_val - b)/a
                return f"Решение: x = {x}"
            else:
                return "Уравнение должно содержать переменную x."
        except Exception as e:
            return f"Ошибка при решении уравнения: {str(e)}"

    def plot_graph(self):
        if self.mode_var.get() != "Построение графика":
            return
        function = self.input_entry.get()
        if self.graph_window and tk.Toplevel.winfo_exists(self.graph_window):
            # обновим график в существующем окне
            self.update_graph(function)
        else:
            self.graph_window = tk.Toplevel(self.master)
            self.graph_window.title("График функции")
            self.graph_window.geometry("800x600")
            self.graph_window.protocol("WM_DELETE_WINDOW", self.on_graph_window_close)

            self.fig, self.ax = plt.subplots(figsize=(8, 6))
            self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_window)
            self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=1)

            self.update_graph(function)

    def update_graph(self, function):
        try:
            x = np.linspace(-10, 10, 400)
            y = eval(function, {"x": x, "np": np})
            self.ax.clear()
            self.ax.plot(x, y, label=f'y = {function}')
            self.ax.set_title('График функции')
            self.ax.set_xlabel('x')
            self.ax.set_ylabel('y')
            self.ax.axhline(0, color='black', linewidth=0.5, ls='--')
            self.ax.axvline(0, color='black', linewidth=0.5, ls='--')
            self.ax.grid(True)
            self.ax.legend()
            self.canvas.draw()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Неверный ввод для графика: {str(e)}")

    def on_graph_window_close(self):
        self.graph_window.destroy()
        self.graph_window = None

if __name__ == "__main__":
    root = tk.Tk()
    app = CalculatorApp(root)
    root.mainloop()
