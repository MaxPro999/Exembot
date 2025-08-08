# init_db.py
import sqlite3
import os
import hashlib
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def create_db(db_name="autoservis_users.db"):
    """
    Создает базу данных и необходимые таблицы.
    Возвращает True при успехе, False при ошибке.
    """
    try:
        conn = sqlite3.connect(db_name)
        cur = conn.cursor()
        
        # Создание таблицы пользователей (без комментариев в SQL)
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                login TEXT UNIQUE NOT NULL,
                password_hash BLOB NOT NULL,
                salt BLOB NOT NULL
            )
        ''')
        
        # Создание таблицы тестов
        cur.execute('''
            CREATE TABLE IF NOT EXISTS table_tests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                object TEXT NOT NULL,
                type TEXT NOT NULL,
                iduser INTEGER NOT NULL,
                count_questions INTEGER NOT NULL,
                FOREIGN KEY (iduser) REFERENCES users(id)
            )
        ''')
        
        # Создание таблицы кодов доступа
        cur.execute('''
            CREATE TABLE IF NOT EXISTS Codes_members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Code TEXT UNIQUE NOT NULL,
                idtest INTEGER NOT NULL,
                used INTEGER DEFAULT 0,
                FOREIGN KEY (idtest) REFERENCES table_tests(id)
            )
        ''')
        
        # Добавление администратора
        add_admin_user(cur)
        
        conn.commit()
        logging.info("База данных успешно создана")
        return True
        
    except sqlite3.Error as e:
        logging.error(f"Ошибка SQLite: {str(e)}")
        return False
    except Exception as e:
        logging.error(f"Неизвестная ошибка: {str(e)}")
        return False
    finally:
        if conn:
            conn.close()

def add_admin_user(cur, login="admin", password="admin"):
    """
    Добавляет администратора в систему.
    Возвращает True если пользователь добавлен или уже существует.
    """
    try:
        # Проверяем существование пользователя
        cur.execute("SELECT 1 FROM users WHERE login = ?", (login,))
        if cur.fetchone():
            logging.info("Администратор уже существует")
            return True
            
        # Генерируем соль и хеш
        salt = os.urandom(32)
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode(),
            salt,
            100000
        )
        
        # Добавляем пользователя
        cur.execute(
            "INSERT INTO users (login, password_hash, salt) VALUES (?, ?, ?)",
            (login, password_hash, salt)
        )
        logging.info("Администратор успешно добавлен")
        return True
        
    except sqlite3.Error as e:
        logging.error(f"Ошибка добавления администратора: {str(e)}")
        return False

if __name__ == "__main__":
    if create_db():
        print("База данных успешно инициализирована")
        print("Данные для входа: admin / admin")
    else:
        print("Ошибка инициализации базы данных")
        exit(1)