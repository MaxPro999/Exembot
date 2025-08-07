# init_db.py
import sqlite3
import os          # Добавлено
import hashlib

def create_db():
    conn = sqlite3.connect('autoservis_users.db')
    cur = conn.cursor()

    # Пользователи
    cur.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        login TEXT UNIQUE NOT NULL,
        password_hash BLOB NOT NULL,
        salt BLOB NOT NULL
    )''')

    # Тесты
    cur.execute('''CREATE TABLE IF NOT EXISTS table_tests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        object TEXT NOT NULL,
        type TEXT NOT NULL,
        iduser INTEGER NOT NULL,
        count_questions INTEGER NOT NULL,
        FOREIGN KEY (iduser) REFERENCES users(id)
    )''')

    # Коды доступа
    cur.execute('''CREATE TABLE IF NOT EXISTS Codes_members (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        Code TEXT UNIQUE NOT NULL,
        idtest INTEGER NOT NULL,
        used INTEGER DEFAULT 0,
        FOREIGN KEY (idtest) REFERENCES table_tests(id)
    )''')

    # Добавляем админа
    add_admin_user(cur)

    conn.commit()
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