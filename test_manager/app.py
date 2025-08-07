# app.py
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from auth import AuthManager
from test_manager import TestManager
import logging
logging.basicConfig(
    filename='app.log', 
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class TestApp:
    def __init__(self):
        self.auth = AuthManager()
        self.test_manager = None
        self.current_window = None
        self.filepath = None
        self.start_window()

    def start_window(self):
        self.destroy_window()
        if not hasattr(self, 'root'):
            self.root = tk.Tk()
            self.current_window = self.root
        self.current_window.title("Вход")
        self.current_window.geometry("450x450")
        self.current_window.resizable(False, False)
        self.current_window.configure(bg="lightblue")

        tk.Label(self.current_window, text="Войти", font=("Arial", 20, "bold"), bg="lightblue").place(x=150, y=50)
        tk.Label(self.current_window, text="Логин:", font=("Arial", 15), bg="lightblue").place(x=50, y=150)
        tk.Label(self.current_window, text="Пароль:", font=("Arial", 15), bg="lightblue").place(x=50, y=200)

        self.login_var = tk.StringVar()
        self.pass_var = tk.StringVar()

        self.login_entry = tk.Entry(self.current_window, textvariable=self.login_var, font=("Arial", 15), width=20)
        self.login_entry.place(x=150, y=150)

        self.pass_entry = tk.Entry(self.current_window, textvariable=self.pass_var, font=("Arial", 15), show="*", width=20)
        self.pass_entry.place(x=150, y=200)

        tk.Button(self.current_window, text="§", font=("Arial", 12), command=lambda: self.toggle_pass(self.pass_entry)).place(x=310, y=200)
        tk.Button(self.current_window, text="Войти", font=("Arial", 15), width=13, command=self.enter).place(x=150, y=300)
        tk.Button(self.current_window, text="Зарегистрироваться", font=("Arial", 15), width=20, command=self.register).place(x=100, y=350)

        self.current_window.mainloop()

    @staticmethod
    def toggle_pass(entry):
        if entry.cget("show") == "*":
            entry.config(show="")
        else:
            entry.config(show="*")

    def enter(self):
        login = self.login_var.get().strip()
        password = self.pass_var.get().strip()
        if not login or not password:
            messagebox.showerror("Ошибка", "Заполните логин и пароль")
            return
        success, msg = self.auth.login(login, password)
        if success:
            self.test_manager = TestManager(self.auth.current_user_id)
            messagebox.showinfo("Успех", msg)
            self.main_window()  # Изменил work_window на main_window
        else:
            messagebox.showerror("Ошибка", msg)

    def main_window(self):
        """Основное рабочее окно после авторизации"""
        self.destroy_window()
        if not hasattr(self, 'root'):
            self.root = tk.Tk()
            self.current_window = self.root
        self.current_window.title("Управление тестами")
        self.current_window.geometry("800x600")
        self.current_window.resizable(False, False)
        self.current_window.configure(bg="lightblue")

        # Frame для загрузки тестов
        load_frame = tk.LabelFrame(self.current_window, text="Загрузка теста", bg="lightblue", font=("Arial", 12))
        load_frame.pack(pady=10, padx=10, fill="x")

        tk.Button(load_frame, text="Выбрать файл", font=("Arial", 12), command=self.load_file).pack(side="left", padx=5)
        
        self.object_var = tk.StringVar()
        self.type_var = tk.StringVar()
        self.code_var = tk.StringVar(value="1")

        tk.Label(load_frame, text="Предмет:", font=("Arial", 12), bg="lightblue").pack(side="left", padx=5)
        tk.Entry(load_frame, textvariable=self.object_var, font=("Arial", 12), width=15).pack(side="left", padx=5)
        
        tk.Label(load_frame, text="Тема:", font=("Arial", 12), bg="lightblue").pack(side="left", padx=5)
        tk.Entry(load_frame, textvariable=self.type_var, font=("Arial", 12), width=15).pack(side="left", padx=5)
        
        tk.Label(load_frame, text="Кол-во кодов:", font=("Arial", 12), bg="lightblue").pack(side="left", padx=5)
        tk.Entry(load_frame, textvariable=self.code_var, font=("Arial", 12), width=5).pack(side="left", padx=5)
        
        tk.Button(load_frame, text="Сохранить тест", font=("Arial", 12), command=self.save_test).pack(side="right", padx=5)

        # Frame для управления тестами
        manage_frame = tk.LabelFrame(self.current_window, text="Управление тестами", bg="lightblue", font=("Arial", 12))
        manage_frame.pack(pady=10, padx=10, fill="x")

        self.combobox = ttk.Combobox(manage_frame, font=("Arial", 12), state="readonly")
        self.combobox.pack(side="left", padx=5, fill="x", expand=True)
        self.update_combobox()

        tk.Button(manage_frame, text="Закрыть тест", font=("Arial", 12), command=self.close_test).pack(side="left", padx=5)
        tk.Button(manage_frame, text="Удалить тест", font=("Arial", 12), command=self.delete_test).pack(side="left", padx=5)
        tk.Button(manage_frame, text="Экспорт результатов", font=("Arial", 12), command=self.export_results).pack(side="left", padx=5)

        # Кнопка выхода
        tk.Button(self.current_window, text="Выйти", font=("Arial", 12), command=self.start_window).pack(side="bottom", pady=10)

        self.current_window.mainloop()

    def register(self):
        login = self.login_var.get().strip()
        password = self.pass_var.get().strip()
        if not login or not password:
            messagebox.showerror("Ошибка", "Заполните логин и пароль")
            return
        success, msg = self.auth.register(login, password)
        messagebox.showinfo("Регистрация", msg)

    def load_file(self):
        self.filepath = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx *.xls")]
        )
        if self.filepath:
            filename = self.filepath.split("/")[-1].split("\\")[-1]  # кроссплатформенно
            messagebox.showinfo("Файл", f"Выбран: {filename}")
        else:
            self.filepath = None

    def save_test(self):
        if not self.filepath:
            messagebox.showerror("Ошибка", "Сначала загрузите файл")
            return
        obj = self.object_var.get().strip()
        typ = self.type_var.get().strip()
        if not obj or not typ:
            messagebox.showerror("Ошибка", "Заполните предмет и тему")
            return

        try:
            count = int(self.code_var.get().strip())
            if count <= 0:
                raise ValueError
        except:
            count = 1
            messagebox.showwarning("Внимание", "Количество участников установлено в 1")

        test_id, msg = self.test_manager.save_test(self.filepath, obj, typ)
        if test_id:
            codes = self.test_manager.generate_access_codes(test_id, count)
            save_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
            if save_path:
                with open(save_path, "w", encoding="utf-8") as f:
                    f.write("Номер;Код\n")
                    for i, c in enumerate(codes, 1):
                        f.write(f"{i};{c}\n")
                messagebox.showinfo("Готово", f"Тест сохранён. Коды экспортированы.")
                self.update_combobox()
        else:
            messagebox.showerror("Ошибка", msg)

    def update_combobox(self):
        if not hasattr(self, 'combobox'):
            return
        tests = self.test_manager.get_user_tests()
        self.combobox['values'] = tests
        if tests:
            self.combobox.current(0)

    def close_test(self):
        sel = self.combobox.get().strip()
        if not sel:
            messagebox.showerror("Ошибка", "Выберите тест")
            return
        if "@" not in sel:
            messagebox.showerror("Ошибка", "Некорректный формат теста")
            return
        try:
            test_id = int(sel.split("@")[-1])
        except:
            messagebox.showerror("Ошибка", "Некорректный ID теста")
            return
        msg = self.test_manager.close_test(test_id)
        messagebox.showinfo("Закрытие", msg)
        self.update_combobox()

    def delete_test(self):
        sel = self.combobox.get().strip()
        if not sel:
            messagebox.showerror("Ошибка", "Выберите тест")
            return
        if "@" not in sel:
            messagebox.showerror("Ошибка", "Некорректный формат теста")
            return
        try:
            test_id = int(sel.split("@")[-1])
        except:
            messagebox.showerror("Ошибка", "Некорректный ID теста")
            return
        msg = self.test_manager.delete_test(test_id)
        messagebox.showinfo("Удаление", msg)
        self.update_combobox()

    def export_results(self):
        sel = self.combobox.get().strip()
        if not sel:
            messagebox.showerror("Ошибка", "Выберите тест")
            return
        if "@" not in sel:
            messagebox.showerror("Ошибка", "Некорректный формат теста")
            return
        try:
            test_id = int(sel.split("@")[-1])
        except:
            messagebox.showerror("Ошибка", "Некорректный ID теста")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if path:
            msg = self.test_manager.export_results(test_id, path)
            messagebox.showinfo("Экспорт", msg)

    def destroy_window(self):
        if self.current_window:
            try:
                self.current_window.destroy()
            except:
                pass
            self.current_window = None


if __name__ == "__main__":
    app = TestApp()