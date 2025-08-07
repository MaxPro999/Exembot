# auth.py
import hashlib
import os
from database import Database
import logging
logging.basicConfig(
    filename='app.log', 
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class AuthManager:
    def __init__(self):
        self.db = Database()
        self.current_user_id = None

    def login(self, login, password):
        user = self.db.query("SELECT id, password_hash, salt FROM users WHERE login = ?", (login,))
        if not user:
            return False, "Пользователь не найден"
        user = user[0]
        stored_hash = user[1]
        salt = user[2]
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100_000)
        if password_hash == stored_hash:
            self.current_user_id = user[0]
            return True, "Добро пожаловать!"
        return False, "Неверный пароль"

    def register(self, login, password):
        if self.db.query("SELECT 1 FROM users WHERE login = ?", (login,)):
            return False, "Логин уже занят"
        salt = os.urandom(32)
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100_000)
        self.db.execute("INSERT INTO users (login, password_hash, salt) VALUES (?, ?, ?)",
                        (login, password_hash, salt))
        return True, "Регистрация успешна"