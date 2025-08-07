"""
Вспомогательные утилиты

Содержит:
- Функции работы с файлами
- Генерацию случайных значений
- Вспомогательные проверки
"""

import pandas as pd
import secrets  # Криптографически безопасный генератор
import os
import logging
from database import Database

# Максимальный размер файла теста (10 МБ)
MAX_FILE_SIZE = 10 * 1024 * 1024

def read_test_file(filepath):
    """
    Читает файл теста (CSV/Excel)
    
    Поддерживает форматы:
    - CSV (разделитель ;)
    - Excel (.xlsx, .xls)
    
    Args:
        filepath: путь к файлу
        
    Returns:
        DataFrame: данные теста
        
    Raises:
        ValueError: при ошибках чтения
    """
    if not filepath:
        raise ValueError("Файл не выбран")
    
    # Проверка размера файла
    file_size = os.path.getsize(filepath)
    if file_size > MAX_FILE_SIZE:
        raise ValueError(f"Файл слишком большой ({file_size} байт). Максимум: {MAX_FILE_SIZE} байт")
    
    # Определение формата по расширению
    ext = os.path.splitext(filepath)[1].lower()
    
    try:
        if ext == ".csv":
            return pd.read_csv(filepath, delimiter=";")
        elif ext in [".xlsx", ".xls"]:
            return pd.read_excel(filepath)
        else:
            raise ValueError("Неподдерживаемый формат")
    except Exception as e:
        logging.exception("Ошибка чтения файла теста")
        raise Exception(f"Ошибка чтения файла: {e}")