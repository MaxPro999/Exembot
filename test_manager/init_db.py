"""
Модуль инициализации базы данных

Создает:
- Таблицы пользователей
- Таблицы тестов
- Тестового пользователя admin
"""

import sqlite3
import os
import hashlib
import logging

def create_db():
    """
    Создает структуру базы данных
    
    Таблицы:
    - users: пользователи системы
    - table_tests: информация о тестах
    - Codes_members: коды доступа к тестам
    """
    try:
        conn = sqlite3.connect('autoservis_users.db')
        cur = conn.cursor()

        # Таблица пользователей
        cur.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            login TEXT UNIQUE NOT NULL,
            password_hash BLOB NOT NULL,  # Хеш пароля
            salt BLOB NOT NULL  # Соль для хеширования
        )''')

        # Таблица тестов
        cur.execute('''CREATE TABLE IF NOT EXISTS table_tests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            object TEXT NOT NULL,  # Предмет теста
            type TEXT NOT NULL,  # Тема теста
            iduser INTEGER NOT NULL,  # Владелец теста
            count_questions INTEGER NOT NULL,  # Количество вопросов
            FOREIGN KEY (iduser) REFERENCES users(id)
        )''')

        # Добавление тестового пользователя
        add_admin_user(cur)

        conn.commit()
        print("База данных успешно создана")
    except Exception as e:
        logging.exception("Ошибка создания БД")
        print(f"Ошибка: {str(e)}")
    finally:
        conn.close()
    print("База данных создана. Админ-пользователь добавлен (admin / admin).")

def add_admin_user(cur):
    login = "admin"
    password = "admin"
    salt = os.urandom(32)  # ✅ Правильно: os.urandom
    password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100_000)

    try:
        cur.execute("INSERT INTO users (login, password_hash, salt) VALUES (?, ?, ?)",
                    (login, password_hash, salt))
    except sqlite3.IntegrityError:
        pass  # Пользователь уже существует

if __name__ == "__main__":
    create_db()