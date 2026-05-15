import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime

# Глобальные переменные
expenses = []
data_file = "expenses.json"

# Загрузка данных при старте
try:
    with open(data_file, "r", encoding="utf-8") as f:
        expenses = json.load(f)
except FileNotFoundError:
    expenses = []

def validate_input(amount_entry, category_entry, date_entry):
    try:
        amount = float(amount_entry.get())
        if amount <= 0:
            raise ValueError("Сумма должна быть положительным числом")

        date_str = date_entry.get()
        datetime.strptime(date_str, "%Y-%m-%d")

        category = category_entry.get()
        if not category:
            raise ValueError("Категория не может быть пустой")

        return True, amount, category, date_str
    except ValueError as e:
        messagebox.showerror("Ошибка", str(e))
        return False, None, None, None

def add_expense(amount_entry, category_entry, date_entry, tree, total_label):
    valid, amount, category, date = validate_input(amount_entry, category_entry, date_entry)
    if valid:
        expense = {"amount": amount, "category": category, "date": date}
        expenses.append(expense)
        save_data()
        update_table(tree, total_label)
        clear_inputs(amount_entry, category_entry, date_entry)

def clear_inputs(amount_entry, category_entry, date_entry):
    amount_entry.delete(0, tk.END)
    category_entry.set("")
    date_entry.delete(0, tk.END)

def update_table(tree, total_label, filtered_expenses=None):
    for item in tree.get_children():
        tree.delete(item)

    expenses_to_show = filtered_expenses if filtered_expenses else expenses
    total = sum(expense["amount"] for expense in expenses_to_show)
    total_label.config(text=f"Общая сумма: {total:.2f} руб.")

    for expense in expenses_to_show:
        tree.insert("", "end", values=(expense["amount"], expense["category"], expense["date"]))

def apply_filter(tree, total_label, filter_category, start_date_filter, end_date_filter):
    filtered = expenses.copy()

    category_filter = filter_category.get()
    if category_filter != "Все":
        filtered = [e for e in filtered if e["category"] == category_filter]

    start_date = start_date_filter.get()
    if start_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            filtered = [e for e in filtered
                        if datetime.strptime(e["date"], "%Y-%m-%d") >= start]
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат даты начала")
            return

    end_date = end_date_filter.get()
    if end_date:
        try:
            end = datetime.strptime(end_date, "%Y-%m-%d")
            filtered = [e for e in filtered
                      if datetime.strptime(e["date"], "%Y-%m-%d") <= end]
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат даты окончания")
            return

    update_table(tree, total_label, filtered)

def reset_filter(tree, total_label, filter_category, start_date_filter, end_date_filter):
    filter_category.set("Все")
    start_date_filter.delete(0, tk.END)
    end_date_filter.delete(0, tk.END)
    update_table(tree, total_label)

def save_data():
    with open(data_file, "w", encoding="utf-8") as f:
        json.dump(expenses, f, ensure_ascii=False, indent=4)

def create_gui():
    window = tk.Tk()
    window.title("Expense Tracker")

    # Поля ввода
    tk.Label(window, text="Сумма:").grid(row=0, column=0, padx=5, pady=5)
    amount_entry = tk.Entry(window)
    amount_entry.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(window, text="Категория:").grid(row=1, column=0, padx=5, pady=5)
    category_entry = ttk.Combobox(
        window,
        values=["Еда", "Транспорт", "Развлечения", "Другое"]
    )
    category_entry.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(window, text="Дата (ГГГГ-ММ-ДД):").grid(row=2, column=0, padx=5, pady=5)

    date_entry = tk.Entry(window)
    date_entry.grid(row=2, column=1, padx=5, pady=5)

    # Кнопка добавления
    tk.Button(
        window,
        text="Добавить расход",
        command=lambda: add_expense(amount_entry, category_entry, date_entry, tree, total_label)
    ).grid(row=3, column=0, columnspan=2, pady=10)

    # Таблица
    columns = ("Сумма", "Категория", "Дата")
    tree = ttk.Treeview(window, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=120)
    tree.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

    # Фильтрация
    tk.Label(window, text="Фильтр по категории:").grid(row=5, column=0, padx=5, pady=5)
    filter_category = ttk.Combobox(
        window,
        values=["Все", "Еда", "Транспорт", "Развлечения", "Другое"]
    )
    filter_category.set("Все")
    filter_category.grid(row=5, column=1, padx=5, pady=5)

    tk.Label(window, text="Период с (ГГГГ-ММ-ДД):").grid(row=6, column=0, padx=5, pady=5)
    start_date_filter = tk.Entry(window)
    start_date_filter.grid(row=6, column=1, padx=5, pady=5)

    tk.Label(window, text="по (ГГГГ-ММ-ДД):").grid(row=7, column=0, padx=5, pady=5)
    end_date_filter = tk.Entry(window)
    end_date_filter.grid(row=7, column=1, padx=5, pady=5)

    tk.Button(
        window,
        text="Применить фильтр",
        command=lambda: apply_filter(tree, total_label, filter_category, start_date_filter, end_date_filter)
    ).grid(row=8, column=0, pady=10)

    tk.Button(
        window,
        text="Сбросить фильтр",
        command=lambda: reset_filter(tree, total_label, filter_category, start_date_filter, end_date_filter)
    ).grid(row=8, column=1, pady=10)

    # Подсчёт суммы
    total_label = tk.Label(window, text="Общая сумма: 0 руб.")
    total_label.grid(row=9, column=0, columnspan=2, pady=5)

    # Первоначальное заполнение таблицы
    update_table(tree, total_label)

    window.mainloop()


if __name__ == "__main__":
    create_gui()
