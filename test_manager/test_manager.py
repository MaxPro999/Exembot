# test_manager.py
from database import Database
from utils import read_test_file, generate_unique_code
import pandas as pd
import logging

class TestManager:
    def __init__(self, user_id):
        self.user_id = user_id
        self.db = Database()

    def get_user_tests(self):
        """Получение списка тестов пользователя"""
        tests = self.db.query(
            "SELECT id, object, type FROM table_tests WHERE iduser = ?", 
            (self.user_id,)
        )
        return [f"{t['object']} - {t['type']}; @{t['id']}" for t in tests] if tests else []

    def save_test(self, filepath, test_object, test_type):
        """Сохранение теста в базу данных"""
        try:
            df = read_test_file(filepath)
            count_questions = len(df)
            
            test_id = self.db.execute(
                "INSERT INTO table_tests (object, type, iduser, count_questions) VALUES (?, ?, ?, ?)",
                (test_object, test_type, self.user_id, count_questions)
            )
            
            if not test_id:
                return None, "Ошибка сохранения теста"
            
            self._create_question_tables(test_id, df)
            return test_id, "Тест сохранён"
            
        except Exception as e:
            logging.exception("Ошибка сохранения теста")
            return None, f"Ошибка сохранения: {str(e)}"

    def _create_question_tables(self, test_id, df):
        """Создание таблиц вопросов для теста"""
        self.db.execute(f"DROP TABLE IF EXISTS Questions{test_id}")
        self.db.execute(f"DROP TABLE IF EXISTS Questions{test_id}_result")

        self.db.execute(f"""
            CREATE TABLE Questions{test_id} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                count_answer TEXT NOT NULL,
                id_answer_true TEXT NOT NULL,
                answer TEXT NOT NULL
            )
        """)
        self.db.execute(f"""
            CREATE TABLE Questions{test_id}_result (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code_member INTEGER NOT NULL,
                question TEXT NOT NULL,
                answer_true TEXT NOT NULL,
                answer TEXT NOT NULL,
                FIO TEXT NOT NULL,
                result TEXT NOT NULL
            )
        """)

        data = []
        for _, row in df.iterrows():
            question = row['question']
            count_ans = int(row['answer_count'])
            true_id = int(row['correct_answer'])
            answers = "; ".join([f"{i}: {row[f'answer{i}']}" for i in range(1, count_ans + 1)])
            data.append((question, str(count_ans), str(true_id), answers))
        
        # Указываем столбцы явно — исключаем `id`
        self.db.executemany(
            f"INSERT INTO Questions{test_id} (question, count_answer, id_answer_true, answer) VALUES (?, ?, ?, ?)",
            data
        )

    def generate_access_codes(self, test_id, count):
        """Генерация кодов доступа для теста"""
        codes = []
        for _ in range(count):
            code = generate_unique_code(self.user_id, test_id)
            self.db.execute(
                "INSERT INTO Codes_members (Code, idtest) VALUES (?, ?)", 
                (code, test_id)
            )
            codes.append(code)
        return codes