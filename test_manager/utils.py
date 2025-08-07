# utils.py
import pandas as pd
import random
import os
from database import Database

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
        raise Exception(f"Ошибка чтения файла: {e}")

def generate_unique_code(id_user, id_test, table="Codes_members"):
    db = Database()
    max_attempts = 100
    for _ in range(max_attempts):
        code = str(id_user) + str(random.randint(10000000, 99999999)) + str(id_test)
        result = db.query(f"SELECT 1 FROM {table} WHERE Code = ?", (code,))
        if not result:
            return code
    raise Exception("Не удалось сгенерировать уникальный код")