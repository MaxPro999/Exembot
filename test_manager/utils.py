# utils.py
import pandas as pd
import secrets  # Для безопасной генерации кодов
import os
import logging
from database import Database

# Максимальный размер файла (10 МБ)
MAX_FILE_SIZE = 10 * 1024 * 1024

def read_test_file(filepath):
    """
    Читает файл теста (CSV/Excel)
    
    Args:
        filepath: путь к файлу теста
        
    Returns:
        DataFrame: данные теста
        
    Raises:
        ValueError: при ошибках чтения файла
    """
    if not filepath:
        raise ValueError("Файл не выбран")
    
    # Проверка размера файла
    file_size = os.path.getsize(filepath)
    if file_size > MAX_FILE_SIZE:
        raise ValueError(f"Файл слишком большой ({file_size} байт). Максимум: {MAX_FILE_SIZE} байт")
    
    ext = os.path.splitext(filepath)[1].lower()
    try:
        if ext == ".csv":
            return pd.read_csv(filepath, delimiter=";")
        elif ext in [".xlsx", ".xls"]:
            return pd.read_excel(filepath)
        else:
            raise ValueError("Неподдерживаемый формат файла")
    except Exception as e:
        logging.exception("Ошибка чтения файла теста")
        raise Exception(f"Ошибка чтения файла: {e}")

def generate_unique_code(id_user, id_test, table="Codes_members"):
    """
    Генерирует уникальный код доступа
    
    Args:
        id_user: ID пользователя
        id_test: ID теста
        table: таблица для проверки уникальности
        
    Returns:
        str: уникальный код доступа
        
    Raises:
        Exception: если не удалось сгенерировать уникальный код
    """
    db = Database()
    max_attempts = 100
    
    for _ in range(max_attempts):
        # Генерируем безопасный случайный код
        code = secrets.token_urlsafe(16)[:16]  # Берем первые 16 символов
        
        # Проверяем уникальность кода в базе
        result = db.query(f"SELECT 1 FROM {table} WHERE Code = ?", (code,))
        if not result:
            return code
    
    logging.error("Не удалось сгенерировать уникальный код")
    raise Exception("Не удалось сгенерировать уникальный код после 100 попыток")