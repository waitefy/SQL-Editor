import sqlite3


class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.cursor = None
        self.db_path = None

    def connect(self, path):
        """Подключение к базе данных"""
        self.connection = sqlite3.connect(path)
        self.cursor = self.connection.cursor()
        self.db_path = path

    def execute_query(self, query):
        """
        Выполнение SQL запроса.
        Возвращает (headers, rows) для SELECT или ([], []) для остальных.
        Выбрасывает ConnectionError или sqlite3.Error.
        """
        if not self.connection:
            raise ConnectionError("Нет активного соединения с базой данных")

        # Выполняем запрос
        self.cursor.execute(query)

        # Если есть описание курсора — это выборка данных (SELECT)
        if self.cursor.description:
            headers = [desc[0] for desc in self.cursor.description]
            rows = self.cursor.fetchall()
            return headers, rows

        # Если описания нет — это команда действия (INSERT, UPDATE, CREATE, DROP)
        else:
            self.connection.commit()
            return [], []

    def close(self):
        """Закрытие соединения"""
        if self.connection:
            self.connection.close()
            self.connection = None
            self.cursor = None
            self.db_path = None

    def get_tables(self):
        """Получение списка таблиц"""
        if not self.connection:
            return []

        query = "SELECT name FROM sqlite_master WHERE type='table';"
        try:
            self.cursor.execute(query)
            # Возвращаем плоский список имен
            return [row[0] for row in self.cursor.fetchall()]
        except sqlite3.Error:
            return []
