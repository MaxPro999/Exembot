"""
Модуль работы с базой данных

Реализует:
- Подключение к SQLite
- Выполнение запросов
- Безопасное управление соединениями
- Обработку ошибок
"""

import sqlite3
import logging

class Database:
    """
    Обертка для работы с SQLite
    
    Обеспечивает:
    - Безопасное подключение (контекстные менеджеры)
    - Логирование ошибок
    - Упрощенный интерфейс запросов
    """
    
    def __init__(self, db_name="autoservis_users.db"):
        """
        Инициализация подключения к БД
        
        Args:
            db_name: имя файла базы данных
        """
        self.db_name = db_name

    def query(self, sql, params=()):
        """
        Выполняет SQL-запрос с возвратом результатов
        
        Args:
            sql: SQL-запрос
            params: параметры запроса
            
        Returns:
            list: список словарей с результатами
            
        Raises:
            sqlite3.Error: при ошибках SQL
        """
        try:
            with sqlite3.connect(self.db_name) as conn:
                conn.row_factory = sqlite3.Row  # Для доступа по имени столбца
                cur = conn.cursor()
                cur.execute(sql, params)
                
                # Для SELECT возвращаем результаты
                if sql.strip().upper().startswith("SELECT"):
                    return [dict(row) for row in cur.fetchall()]
                return None
                
        except sqlite3.Error as e:
            logging.error(f"Ошибка SQLite: {e}")
            raise   