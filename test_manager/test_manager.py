"""
Модуль управления тестами

Функционал:
- Создание/удаление тестов
- Генерация кодов доступа
- Экспорт результатов
- Управление вопросами тестов
"""
# test_manager.py
from database import Database
from utils import read_test_file, generate_unique_code  # Этот импорт теперь должен работать
import pandas as pd
import logging

class TestManager:
    """
    Менеджер работы с тестами
    
    Реализует:
    - Хранение тестов в БД
    - Управление структурой тестов
    - Генерацию уникальных кодов доступа
    - Экспорт результатов
    """
    
    def __init__(self, user_id):
        """
        Инициализация менеджера тестов
        
        Args:
            user_id: ID пользователя-владельца тестов
        """
        self.user_id = user_id
        self.db = Database()  # Объект для работы с БД

    def save_test(self, filepath, test_object, test_type):
        """
        Сохраняет тест в базу данных
        
        Алгоритм:
        1. Чтение файла теста
        2. Создание записи в таблице тестов
        3. Создание таблиц вопросов
        4. Импорт вопросов из файла
        
        Args:
            filepath: путь к файлу теста
            test_object: предмет теста (например, "Математика")
            test_type: тема теста (например, "Квадратные уравнения")
            
        Returns:
            tuple: (test_id, сообщение)
        """
        try:
            # Чтение файла теста
            df = read_test_file(filepath)
            
            # Создание записи о тесте
            count_questions = len(df)
            test_id = self.db.execute(
                "INSERT INTO table_tests (object, type, iduser, count_questions) VALUES (?, ?, ?, ?)",
                (test_object, test_type, self.user_id, count_questions)
            )
            
            if not test_id:
                return None, "Ошибка сохранения теста"

            # Создание структуры для вопросов
            self._create_question_tables(test_id, df)
            return test_id, "Тест сохранён"
            
        except Exception as e:
            logging.exception("Ошибка сохранения теста")
            return None, f"Ошибка сохранения: {str(e)}"

    def _create_question_tables(self, test_id, df):
        """
        Создает таблицы для хранения вопросов теста
        
        Args:
            test_id: ID теста
            df: DataFrame с вопросами
            
        Создает:
        - Таблицу Questions{test_id} - вопросы теста
        - Таблицу Questions{test_id}_result - результаты
        """
        if not self._is_valid_test_id(test_id):
            raise ValueError("Некорректный ID теста")
        
        try:
            # Удаление старых таблиц (если есть)
            self.db.execute(f"DROP TABLE IF EXISTS Questions{test_id}")
            self.db.execute(f"DROP TABLE IF EXISTS Questions{test_id}_result")

            # Создание таблицы вопросов
            self.db.execute(f"""
                CREATE TABLE Questions{test_id} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question TEXT NOT NULL,
                    count_answer TEXT NOT NULL,
                    id_answer_true TEXT NOT NULL,
                    answer TEXT NOT NULL
                )
            """)

            # Создание таблицы результатов
            self.db.execute(f"""
                CREATE TABLE Questions{test_id}_result (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question TEXT NOT NULL,
                    answer_true TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    result TEXT NOT NULL,
                    FIO TEXT NOT NULL,
                    code_member TEXT NOT NULL
                )
            """)
            
            # Массовая вставка вопросов
            data = []
            for _, row in df.iterrows():
                question = row[0]
                count_ans = str(row[1])
                true_id = str(row[2])
                answers = "; ".join([f"{i}: {row[i]}" for i in range(3, 3 + int(count_ans))])
                data.append((question, count_ans, true_id, answers))
            
            self.db.executemany(
                f"INSERT INTO Questions{test_id} VALUES (?, ?, ?, ?)",
                data
            )
            
        except Exception as e:
            logging.exception("Ошибка создания таблиц вопросов")
            raise