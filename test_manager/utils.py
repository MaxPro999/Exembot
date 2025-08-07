# utils.py
import pandas as pd
import random
import os
from database import Database
import secrets
import logging
logging.basicConfig(
    filename='app.log', 
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def read_test_file(filepath):
    if not filepath:
        raise ValueError("Файл не выбран")
    ext = os.path.splitext(filepath)[1].lower()
    try:
        if ext == ".csv":
            return pd.read_csv(filepath, delimiter=";")
        elif ext in [".xlsx", ".xls"]:
            return pd.read_excel(filepath)
        else:
            raise ValueError("Неподдерживаемый формат")
    except Exception as e:
        logging.exception(f"Ошибка чтения файла: {e}")
        raise Exception(f"Ошибка чтения файла: {e}")


def generate_unique_code(id_user, id_test, table="Codes_members"):
    db = Database()
    max_attempts = 100
    for _ in range(max_attempts):
        code = secrets.token_urlsafe(12)  # 16-символьный безопасный токен
        result = db.query(f"SELECT 1 FROM {table} WHERE Code = ?", (code,))
        if not result:
            return code
    raise Exception("Не удалось сгенерировать уникальный код")