"""
Главный модуль приложения для управления тестами

Содержит:
- Класс TestApp - основной класс приложения
- Методы для работы с GUI (окна входа, основное окно)
- Обработчики событий
- Логику взаимодействия с другими модулями
"""

import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from auth import AuthManager
from test_manager import TestManager
import logging

# Настройка системы логирования
logging.basicConfig(
    filename='app.log', 
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class TestApp:
    """
    Основной класс приложения, реализующий графический интерфейс
    
    Атрибуты:
    - auth: менеджер аутентификации
    - test_manager: менеджер работы с тестами 
    - current_window: текущее активное окно
    - filepath: путь к выбранному файлу теста
    """
    
    def __init__(self):
        """Инициализация приложения - создание окна входа"""
        self.auth = AuthManager()
        self.test_manager = None
        self.current_window = None
        self.filepath = None
        self.start_window()

    def start_window(self):
        """
        Создает окно входа в систему
        
        Содержит:
        - Поля для ввода логина/пароля
        - Кнопки входа и регистрации
        - Кнопку показа/скрытия пароля
        """
        self.destroy_window()
        
        # Основные настройки окна
        self.current_window = tk.Tk()
        self.current_window.title("Вход")
        self.current_window.geometry("450x450")
        self.current_window.resizable(False, False)
        self.current_window.configure(bg="lightblue")

        # Элементы интерфейса
        tk.Label(self.current_window, text="Войти", font=("Arial", 20, "bold"), bg="lightblue").place(x=150, y=50)
        
        # Поля ввода
        self.login_var = tk.StringVar()
        self.pass_var = tk.StringVar()
        
        # Кнопка переключения видимости пароля
        tk.Button(self.current_window, text="§", font=("Arial", 12), 
                command=lambda: self.toggle_pass(self.pass_entry)).place(x=310, y=200)
        
        # Основной цикл обработки событий
        self.current_window.mainloop()

    def main_window(self):
        """
        Основное рабочее окно после успешного входа
        
        Содержит:
        - Панель загрузки новых тестов
        - Панель управления существующими тестами
        - Кнопку выхода из системы
        """
        try:
            self.destroy_window()
            self.current_window = tk.Tk()
            
            # Создаем два основных фрейма
            load_frame = self.create_load_frame()  # Для загрузки тестов
            manage_frame = self.create_manage_frame()  # Для управления тестами
            
            # Размещаем фреймы в окне
            load_frame.pack(pady=10, padx=10, fill="x")
            manage_frame.pack(pady=10, padx=10, fill="x")
            
            self.current_window.mainloop()
        except Exception as e:
            logging.exception("Ошибка в main_window")
            messagebox.showerror("Ошибка", f"Не удалось создать главное окно: {str(e)}")

    def save_test(self):
        """
        Сохраняет тест в базу данных
        
        Логика работы:
        1. Проверяет наличие выбранного файла
        2. Валидирует введенные данные (предмет, тему)
        3. Проверяет количество кодов доступа
        4. Сохраняет тест через TestManager
        5. Генерирует коды доступа
        6. Предлагает сохранить коды в файл
        """
        try:
            # Проверка наличия файла
            if not self.filepath:
                messagebox.showerror("Ошибка", "Сначала загрузите файл")
                return
                
            # Валидация входных данных
            obj = self.object_var.get().strip()
            typ = self.type_var.get().strip()
            if not obj or not typ:
                messagebox.showerror("Ошибка", "Заполните предмет и тему")
                return

            # Обработка количества кодов
            try:
                count = int(self.code_var.get().strip())
                if count <= 0:
                    raise ValueError("Количество должно быть положительным")
                if count > 1000:
                    messagebox.showwarning("Внимание", "Максимальное количество кодов - 1000")
                    count = 1000
            except ValueError as ve:
                count = 1
                messagebox.showwarning("Внимание", f"Некорректное количество. Установлено значение 1. Ошибка: {str(ve)}")

            # Сохранение теста через менеджер
            test_id, msg = self.test_manager.save_test(self.filepath, obj, typ)
            if not test_id:
                messagebox.showerror("Ошибка", msg)
                return

            # Генерация и сохранение кодов
            codes = self.test_manager.generate_access_codes(test_id, count)
            save_path = filedialog.asksaveasfilename(
                defaultextension=".csv", 
                filetypes=[("CSV files", "*.csv")]
            )
            if save_path:
                with open(save_path, "w", encoding="utf-8") as f:
                    f.write("Номер;Код\n")
                    for i, c in enumerate(codes, 1):
                        f.write(f"{i};{c}\n")
                messagebox.showinfo("Готово", "Тест сохранён. Коды экспортированы.")
                self.update_combobox()
                
        except Exception as e:
            logging.exception("Ошибка в save_test")
            messagebox.showerror("Ошибка", f"Не удалось сохранить тест: {str(e)}")