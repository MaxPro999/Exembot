# database.py
import sqlite3
import logging
logging.basicConfig(
    filename='app.log', 
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class Database:
    def __init__(self, db_name="autoservis_users.db"):
        self.db_name = db_name

    def query(self, sql, params=()):
        conn = sqlite3.connect(self.db_name)
        cur = conn.cursor()
        try:
            cur.execute(sql, params)
            if sql.strip().upper().startswith("SELECT"):
                return cur.fetchall()
            conn.commit()
        except Exception as e:
            logging.exception(f"Ошибка БД: {e}")
            return None
        finally:
            conn.close()

    def execute(self, sql, params=()):
        conn = sqlite3.connect(self.db_name)
        cur = conn.cursor()
        try:
            cur.execute(sql, params)
            conn.commit()
            return cur.lastrowid
        except Exception as e:
            logging.exception(f"Ошибка выполнения: {e}")
            return None
        finally:
            conn.close()