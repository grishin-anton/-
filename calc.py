import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# Открытие окна калькулятора
def open_calculator():
    calc_window = tk.Toplevel(root)
    calc_window.title("Калькулятор")
    calc_window.geometry("300x400")

    # Поле для ввода выражения
    entry_field = tk.Entry(calc_window, width=25, font=("Arial", 18), justify='right')
    entry_field.grid(row=0, column=0, columnspan=4, pady=10)

    # Обработка нажатия кнопки числа/оператора
    def press_button(symbol):
        entry_field.insert(tk.END, symbol)

    # Очистка поля ввода
    def clear_input():
        entry_field.delete(0, tk.END)

    # Вычисление выражения
    def evaluate_expression():
        try:
            expr = entry_field.get().replace("^", "**")
            # Определяем функции для поддержки математических функций
            math_functions = {
                "sin": np.sin,
                "cos": np.cos,
                "log": np.log,
                "sqrt": np.sqrt,
                "exp": np.exp,
                "x": None  # переменная x для графиков
            }
            result = eval(expr, math_functions)
            entry_field.delete(0, tk.END)
            entry_field.insert(tk.END, str(result))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Некорректный ввод: {e}")

    # Создание кнопок калькулятора
    buttons_symbols = [
        "7", "8", "9", "+",
        "4", "5", "6", "-",
        "1", "2", "3", "*",
        "0", ".", "/", "="
    ]

    for idx, symbol in enumerate(buttons_symbols):
        def create_command(s=symbol):
            if s == "=":
                return evaluate_expression
            else:
                return lambda: press_button(s)

        btn = tk.Button(calc_window, text=symbol, width=5, height=2, font=("Arial", 14), command=create_command())
        btn.grid(row=1 + idx // 4, column=idx % 4)

    # Кнопка очистки
    tk.Button(calc_window, text="C", width=5, height=2, font=("Arial", 14), command=clear_input).grid(row=5, column=0)


# Открытие окна решения уравнений
def open_equation_solver():
    solver_window = tk.Toplevel(root)
    solver_window.title("Решение уравнений")
    solver_window.geometry("300x300")

    tk.Label(solver_window, text="Выберите тип уравнения:").pack(pady=10)

    # Решение линейного уравнения
    def solve_linear_equation():
        a = get_numeric_input("Введите коэффициент a:")
        b = get_numeric_input("Введите коэффициент b:")
        if a is not None and b is not None:
            if a == 0 and b == 0:
                result_text = "Уравнение имеет бесконечно много решений"
            elif a == 0:
                result_text = "Уравнение не имеет решений"
            else:
                x_solution = -b / a
                result_text = f"Решение линейного уравнения: x = {x_solution}"
            messagebox.showinfo("Результат", result_text)

    # Решение квадратного уравнения
    def solve_quadratic_equation():
        a = get_numeric_input("Введите коэффициент a:")
        b = get_numeric_input("Введите коэффициент b:")
        c = get_numeric_input("Введите коэффициент c:")
        if None not in (a, b, c):
            discriminant = b ** 2 - 4 * a * c
            if a == 0:
                # Это превращается в линейное уравнение
                solve_linear_equation()
            elif discriminant > 0:
                sqrt_D = discriminant ** 0.5
                x1 = (-b + sqrt_D) / (2 * a)
                x2 = (-b - sqrt_D) / (2 * a)
                messagebox.showinfo("Результат", f"Два решения: x1 = {x1}, x2 = {x2}")
            elif discriminant == 0:
                x = -b / (2 * a)
                messagebox.showinfo("Результат", f"Одно решение: x = {x}")
            else:
                messagebox.showinfo("Результат", "Нет действительных решений")

    # Кнопки для выбора типа уравнения
    tk.Button(solver_window, text="Линейное уравнение", font=("Arial", 12), command=solve_linear_equation).pack(pady=5)
    tk.Button(solver_window, text="Квадратное уравнение", font=("Arial", 12), command=solve_quadratic_equation).pack(
        pady=5)


# Вспомогательная функция для получения числового ввода
def get_numeric_input(prompt):
    input_window = tk.Toplevel(root)
    input_window.title("Ввод числа")
    input_window.geometry("250x100")
    tk.Label(input_window, text=prompt).pack(pady=5)
    entry_field = tk.Entry(input_window)
    entry_field.pack(pady=5)

    result_value = tk.DoubleVar()

    def submit():
        try:
            value = float(entry_field.get())
            result_value.set(value)
            input_window.destroy()
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректное число!")

    tk.Button(input_window, text="OK", command=submit).pack()
    input_window.wait_window()
    # Возвращаем число или None, если ввод некорректен
    return result_value.get() if entry_field.get() != "" else None


# Открытие окна построения графика
def open_graph_plotter():
    plot_window = tk.Toplevel(root)
    plot_window.title("Построение графика")
    plot_window.geometry("500x500")

    # Поле для ввода функции
    func_entry = tk.Entry(plot_window, font=("Arial", 12))
    func_entry.pack(pady=10)
    func_entry.insert(0, "x^2 + sin(x)")

    # Создаем фигуру для графика
    fig, ax = plt.subplots(figsize=(4, 4))
    canvas = FigureCanvasTkAgg(fig, master=plot_window)
    canvas.get_tk_widget().pack()

    def plot_function():
        expr_str = func_entry.get().replace("^", "**")
        functions_dict = {
            "x": None,
            "sin": np.sin,
            "cos": np.cos,
            "log": np.log,
            "sqrt": np.sqrt,
            "exp": np.exp
        }
        try:
            def evaluate_func(x):
                functions_dict["x"] = x
                return eval(expr_str, functions_dict)

            x_vals = np.linspace(-10, 10, 400)
            y_vals = evaluate_func(x_vals)

            ax.clear()
            ax.plot(x_vals, y_vals)
            ax.set_xlabel("x")
            ax.set_ylabel("f(x)")
            ax.grid(True)
            ax.set_title("График функции")
            canvas.draw()
        except Exception as e:
            ax.clear()
            ax.text(0.5, 0.5, f"Ошибка: {e}", ha='center', va='center', fontsize=10)
            canvas.draw()

    tk.Button(plot_window, text="Построить график", font=("Arial", 12), command=plot_function).pack(pady=5)


# Основное окно
root = tk.Tk()
root.title("Многофункциональный калькулятор")
root.geometry("300x250")

tk.Label(root, text="Выберите действие:", font=("Arial", 14)).pack(pady=15)

tk.Button(root, text="Калькулятор", width=20, font=("Arial", 12), command=open_calculator).pack(pady=5)
tk.Button(root, text="Решение уравнений", width=20, font=("Arial", 12), command=open_equation_solver).pack(pady=5)
tk.Button(root, text="Построение графиков", width=20, font=("Arial", 12), command=open_graph_plotter).pack(pady=5)
tk.Button(root, text="Выход", width=20, font=("Arial", 12), command=root.destroy).pack(pady=20)

root.mainloop()