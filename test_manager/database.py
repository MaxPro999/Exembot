# database.py
import sqlite3
import logging

class Database:
    def __init__(self, db_name="autoservis_users.db"):
        self.db_name = db_name

    def query(self, sql, params=()):
        """Выполняет запрос с возвратом результатов"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_name)
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute(sql, params)
            return [dict(row) for row in cur.fetchall()]
        except Exception as e:
            logging.error(f"Query error: {str(e)}")
            return None
        finally:
            if conn:
                conn.close()

    def execute(self, sql, params=()):
        """Выполняет команду (INSERT/UPDATE/DELETE)"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_name)
            cur = conn.cursor()
            cur.execute(sql, params)
            conn.commit()
            return cur.lastrowid
        except Exception as e:
            logging.error(f"Execute error: {str(e)}")
            return None
        finally:
            if conn:
                conn.close()

    def executemany(self, sql, params_list):
        """Выполняет команду для списка параметров (например, массовая вставка)"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_name)
            cur = conn.cursor()
            cur.executemany(sql, params_list)
            conn.commit()
            return cur.lastrowid  # вернёт ID последней вставленной строки
        except Exception as e:
            logging.error(f"Executemany error: {str(e)}")
            return None
        finally:
            if conn:
                conn.close()