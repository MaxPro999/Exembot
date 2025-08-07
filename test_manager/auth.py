# auth.py
import hashlib
import os
import logging
from database import Database

class AuthManager:
    def __init__(self):
        self.db = Database()
        self.current_user_id = None
        self._create_tables()  # Добавляем создание таблиц при инициализации

    def _create_tables(self):
        """Создает необходимые таблицы, если они не существуют"""
        self.db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                login TEXT UNIQUE NOT NULL,
                password_hash BLOB NOT NULL,
                salt BLOB NOT NULL
            )
        ''')

    def login(self, login, password):
        """Аутентификация пользователя"""
        try:
            user = self.db.query(
                "SELECT id, password_hash, salt FROM users WHERE login = ?", 
                (login,)
            )
            
            if not user:
                return False, "Пользователь не найден"
                
            user = user[0]
            stored_hash = user['password_hash']
            salt = user['salt']
            
            input_hash = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode(),
                salt,
                100000
            )
            
            if input_hash == stored_hash:
                self.current_user_id = user['id']
                return True, "Добро пожаловать!"
            return False, "Неверный пароль"
        except Exception as e:
            logging.error(f"Login error: {str(e)}")
            return False, f"Ошибка входа: {str(e)}"

    def register(self, login, password):
        """Регистрация нового пользователя"""
        try:
            # Проверка существования пользователя
            if self.db.query("SELECT 1 FROM users WHERE login = ?", (login,)):
                return False, "Логин уже занят"
            
            # Генерация соли и хеша
            salt = os.urandom(32)
            password_hash = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode(),
                salt,
                100000
            )
            
            # Сохранение пользователя
            user_id = self.db.execute(
                "INSERT INTO users (login, password_hash, salt) VALUES (?, ?, ?)",
                (login, password_hash, salt)
            )
            
            if user_id:
                return True, "Регистрация успешна"
            return False, "Ошибка регистрации"
        except Exception as e:
            logging.error(f"Registration error: {str(e)}")
            return False, f"Ошибка регистрации: {str(e)}"