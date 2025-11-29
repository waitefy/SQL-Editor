import sqlite3
import os


class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.cursor = None
        self.db_path = None

    def connect(self, path):
        """Подключение к БД"""
        try:
            self.connection = sqlite3.connect(path)
            self.cursor = self.connection.cursor()
            self.db_path = path
            return True, f"Успешное подключение: {os.path.basename(path)}"
        except sqlite3.Error as e:
            return False, f"Ошибка подключения: {e}"

    def execute_query(self, query):
        """Выполнение SQL запроса"""
        if not self.connection:
            return None, None, "Нет активного соединения"

        try:
            self.cursor.execute(query)

            # Если это SELECT - получаем данные
            if self.cursor.description:
                headers = [description[0] for description in self.cursor.description]
                rows = self.cursor.fetchall()
                return headers, rows, "Запрос выполнен"
            else:
                # Если это INSERT/UPDATE/CREATE - сохраняем изменения
                self.connection.commit()
                return [], [], "Операция выполнена успешно"

        except sqlite3.Error as e:
            return None, None, f"SQL Ошибка: {e}"

    def get_tables(self):
        """Получение списка таблиц для дерева"""
        if not self.connection:
            return []

        query = "SELECT name FROM sqlite_master WHERE type='table';"
        try:
            self.cursor.execute(query)
            tables = [row[0] for row in self.cursor.fetchall()]
            return tables
        except sqlite3.Error:
            return []

    def close(self):
        if self.connection:
            self.connection.close()