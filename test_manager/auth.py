"""
Модуль аутентификации пользователей

Реализует:
- Вход в систему (логин)
- Регистрацию новых пользователей
- Хранение учетных данных
- Защиту от brute-force атак
"""

import hashlib
import os
import logging
from database import Database

# Ограничение попыток входа для защиты от брутфорса
MAX_LOGIN_ATTEMPTS = 5
login_attempts = {}  # Словарь для хранения неудачных попыток

class AuthManager:
    """
    Менеджер аутентификации
    
    Реализует безопасное хранение паролей с использованием:
    - Соли (salt)
    - Многократного хеширования (PBKDF2)
    - Защиты от перебора
    """
    
    def __init__(self):
        self.db = Database()
        self.current_user_id = None  # ID текущего пользователя

    def login(self, login, password):
        """
        Аутентификация пользователя
        
        Алгоритм работы:
        1. Проверка количества попыток входа
        2. Поиск пользователя в БД
        3. Проверка хеша пароля
        4. Обновление счетчика попыток
        
        Возвращает:
        - (True, сообщение) при успехе
        - (False, сообщение) при ошибке
        """
        # Защита от brute-force
        if login in login_attempts and login_attempts[login] >= MAX_LOGIN_ATTEMPTS:
            return False, "Превышено количество попыток входа. Попробуйте позже."
        
        try:
            # Поиск пользователя в БД
            user = self.db.query(
                "SELECT id, password_hash, salt FROM users WHERE login = ?", 
                (login,)
            )
            
            if not user:
                self._record_failed_attempt(login)
                return False, "Пользователь не найден"
                
            user = user[0]
            
            # Проверка пароля
            stored_hash = user['password_hash']
            salt = user['salt']
            
            # Генерация хеша для введенного пароля
            input_hash = hashlib.pbkdf2_hmac(
                'sha256', 
                password.encode(), 
                salt, 
                310_000  # Количество итераций
            )
            
            # Сравнение хешей
            if input_hash == stored_hash:
                self.current_user_id = user['id']
                # Сброс счетчика при успешном входе
                if login in login_attempts:
                    del login_attempts[login]
                return True, "Добро пожаловать!"
                
            self._record_failed_attempt(login)
            return False, "Неверный пароль"
            
        except Exception as e:
            logging.exception("Ошибка при входе")
            return False, f"Ошибка аутентификации: {str(e)}"

    def _record_failed_attempt(self, login):
        """Увеличивает счетчик неудачных попыток входа"""
        if login not in login_attempts:
            login_attempts[login] = 0
        login_attempts[login] += 1