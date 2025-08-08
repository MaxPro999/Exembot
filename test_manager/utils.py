# utils.py
import pandas as pd
import secrets
import os
import logging
from database import Database

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def read_test_file(filepath):
    """
    Читает и проверяет файл с тестом (CSV или Excel)
    
    Args:
        filepath: Путь к файлу с тестом
        
    Returns:
        pandas.DataFrame: DataFrame с вопросами и ответами
        
    Raises:
        ValueError: Если файл не соответствует требованиям
        Exception: При ошибках чтения файла
        
    Формат файла:
        Обязательные колонки:
        - question: текст вопроса
        - answer_count: количество ответов (2-4)
        - correct_answer: номер правильного ответа (1-4)
        
        Опциональные колонки (answer1, answer2, answer3, answer4): тексты ответов
    """
    # Проверка существования файла
    if not os.path.exists(filepath):
        raise ValueError("Файл не существует")
    
    # Проверка размера файла (не более 10MB)
    file_size = os.path.getsize(filepath)
    if file_size > 10 * 1024 * 1024:  # 10MB
        raise ValueError("Файл слишком большой (максимум 10MB)")
    
    # Определение формата файла
    ext = os.path.splitext(filepath)[1].lower()
    
    try:
        # Чтение файла в зависимости от формата
        if ext == '.csv':
            df = pd.read_csv(filepath, delimiter=';')
        elif ext in ('.xlsx', '.xls'):
            df = pd.read_excel(filepath)
        else:
            raise ValueError("Поддерживаются только CSV и Excel файлы")
        
        # Проверка обязательных колонок
        required_columns = ['question', 'answer_count', 'correct_answer']
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Отсутствуют обязательные колонки: {', '.join(missing_cols)}")
        
        # Проверка каждой строки
        for idx, row in df.iterrows():
            # Проверка вопроса
            if not isinstance(row['question'], str) or not row['question'].strip():
                raise ValueError(f"Строка {idx+1}: Вопрос должен быть непустым текстом")
            
            # Проверка количества ответов
            try:
                answer_count = int(row['answer_count'])
                if not 1 <= answer_count:
                    raise ValueError
            except (ValueError, TypeError):
                raise ValueError(f"Строка {idx+1}: Количество ответов должно быть целым числом больше 0")
            
            # Проверка правильного ответа
            try:
                correct = int(row['correct_answer'])
                if not 1 <= correct <= answer_count:
                    raise ValueError
            except (ValueError, TypeError):
                raise ValueError(f"Строка {idx+1}: Номер правильного ответа должен быть от 1 до {answer_count}")
            
            # Проверка текстов ответов
            for i in range(1, answer_count + 1):
                col = f'answer{i}'
                if col not in df.columns or not isinstance(row[col], str) or not row[col].strip():
                    raise ValueError(f"Строка {idx+1}: Ответ {i} должен быть непустым текстом")
        
        return df
    
    except pd.errors.EmptyDataError:
        raise ValueError("Файл пустой или содержит некорректные данные")
    except pd.errors.ParserError:
        raise ValueError("Ошибка чтения файла. Проверьте формат и кодировку")
    except Exception as e:
        raise ValueError(f"Ошибка обработки файла: {str(e)}")
    

def generate_unique_code(id_user, id_test, table="Codes_members"):
    """
    Генерация уникального кода доступа
    
    Args:
        id_user: ID пользователя
        id_test: ID теста
        table: таблица для проверки уникальности
        
    Returns:
        str: уникальный код
        
    Raises:
        Exception: если не удалось сгенерировать уникальный код
    """
    db = Database()
    max_attempts = 100
    
    for _ in range(max_attempts):
        code = secrets.token_urlsafe(16)[:16]  # Генерация 16-символьного кода
        result = db.query(f"SELECT 1 FROM {table} WHERE Code = ?", (code,))
        if not result:
            return code
    
    logging.error("Не удалось сгенерировать уникальный код")
    raise Exception("Не удалось сгенерировать уникальный код после 100 попыток")