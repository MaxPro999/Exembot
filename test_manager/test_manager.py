# test_manager.py
from database import Database
from utils import read_test_file, generate_unique_code
import pandas as pd
import os
import logging
logging.basicConfig(
    filename='app.log', 
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class TestManager:
    def __init__(self, user_id):
        self.user_id = user_id
        self.db = Database()

    def get_user_tests(self):
        tests = self.db.query(
            "SELECT id, object, type FROM table_tests WHERE iduser = ?", (self.user_id,)
        )
        return [f"{t[1]} - {t[2]}; @{t[0]}" for t in tests]

    def save_test(self, filepath, test_object, test_type):
        try:
            df = read_test_file(filepath)
        except Exception as e:
            logging.exception(e)
            return None, str(e)

        # Создаём запись в таблице тестов
        count_questions = len(df)
        test_id = self.db.execute(
            "INSERT INTO table_tests (object, type, iduser, count_questions) VALUES (?, ?, ?, ?)",
            (test_object, test_type, self.user_id, count_questions)
        )
        if not test_id:
            logging.exception("Ошибка сохранения теста")
            return None, "Ошибка сохранения теста"

        # Создаём таблицы вопросов
        self._create_question_tables(test_id, df)
        return test_id, "Тест сохранён"

    def _create_question_tables(self, test_id, df):
        db = Database()
        if not str(test_id).isdigit():
            raise ValueError("Invalid test ID")
        db.execute(f"DROP TABLE IF EXISTS Questions?",(test_id,))
        db.execute(f"DROP TABLE IF EXISTS Questions?",(test_id,),"_result")

        db.execute(f"""
            CREATE TABLE Questions{test_id} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                count_answer TEXT NOT NULL,
                id_answer_true TEXT NOT NULL,
                answer TEXT NOT NULL
            )
        """)

        db.execute(f"""
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

        for _, row in df.iterrows():
            question = row[0]
            count_ans = str(row[1])
            true_id = str(row[2])
            answers = "; ".join([f"{i}: {row[i]}" for i in range(3, 3 + int(count_ans))])
            if not str(test_id).isdigit():
                raise ValueError("Invalid test ID")
            db.execute(
                "INSERT INTO Questions?",(test_id,), "(question, count_answer, id_answer_true, answer) VALUES (?, ?, ?, ?)",
                (question, count_ans, true_id, answers)
            )

    def generate_access_codes(self, test_id, count):
        codes = []
        for _ in range(count):
            code = generate_unique_code(self.user_id, test_id)
            self.db.execute("INSERT INTO Codes_members (Code, idtest) VALUES (?, ?)", (code, test_id))
            codes.append(code)
        return codes

    def export_results(self, test_id, filepath):
        rows = self.db.query(f"SELECT * FROM Questions{test_id}_result ORDER BY FIO, id")
        if not rows:
            return "Нет результатов"
        df = pd.DataFrame(rows, columns=["id", "question", "answer_true", "answer", "result", "FIO", "code_member"])
        df.to_csv(filepath, sep=";", index=False, encoding="utf-8")
        return "Результаты экспортированы"

    def close_test(self, test_id):
        if not str(test_id).isdigit():
            raise ValueError("Invalid test ID")
        self.db.execute("DROP TABLE IF EXISTS Questions?", (test_id,))
        self.db.execute("DELETE FROM Codes_members WHERE idtest = ?", (test_id,))
        return "Тест закрыт"

    def delete_test(self, test_id):
        self.db.execute(f"DROP TABLE IF EXISTS Questions{test_id}_result")
        self.db.execute("DELETE FROM table_tests WHERE id = ?", (test_id,))
        return "Тест удалён"