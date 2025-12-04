import pytest
import sqlite3
from sql_editor.db.connection import DatabaseManager


class TestCoreLogic:
    """
    Набор тестов для проверки ядра обработки данных.
    Проверяет класс DatabaseManager без участия GUI.
    """

    @pytest.fixture
    def db_manager(self, tmp_path):
        """Создает временную БД и менеджер соединений."""
        db_file = tmp_path / "test_core.db"
        manager = DatabaseManager()
        manager.connect(str(db_file))
        return manager

    def test_connection_properties(self, db_manager):
        """Тестирует свойства активного соединения."""
        assert db_manager.connection is not None
        assert db_manager.cursor is not None
        assert str(db_manager.db_path).endswith("test_core.db")

    def test_create_and_insert(self, db_manager):
        """Тестирует транзакции (CREATE, INSERT)."""
        # 1. Создание таблицы
        headers, rows = db_manager.execute_query(
            "CREATE TABLE heroes (id INTEGER PRIMARY KEY, name TEXT, power TEXT)"
        )
        # Ожидаем пустые списки, так как это не SELECT
        assert headers == []
        assert rows == []

        # 2. Вставка данных
        headers, rows = db_manager.execute_query(
            "INSERT INTO heroes (name, power) VALUES ('Tony Stark', 'Engineering')"
        )
        assert headers == []
        assert rows == []

    def test_select_data(self, db_manager):
        """Тестирует выборку данных (SELECT)."""
        # Подготовка
        db_manager.execute_query("CREATE TABLE users (id INT, name TEXT)")
        db_manager.execute_query("INSERT INTO users VALUES (1, 'Admin')")

        # Выполнение
        headers, rows = db_manager.execute_query("SELECT * FROM users")

        # Проверка
        assert headers == ['id', 'name']
        assert len(rows) == 1
        assert rows[0][1] == 'Admin'

    def test_invalid_query(self, db_manager):
        """Тестирует перехват ошибок SQL."""
        # Ожидаем, что метод выбросит исключение sqlite3.Error
        with pytest.raises(sqlite3.Error):
            db_manager.execute_query("SELECT * FROM non_existent_table")

    def test_no_connection_error(self):
        """Тестирует попытку запроса без подключения."""
        manager = DatabaseManager()
        # Ожидаем ConnectionError
        with pytest.raises(ConnectionError):
            manager.execute_query("SELECT 1")

    def test_close_connection(self, db_manager):
        """Тестирует закрытие соединения."""
        db_manager.close()
        assert db_manager.connection is None

        # Проверяем, что запрос после закрытия вызывает ошибку
        with pytest.raises(ConnectionError):
            db_manager.execute_query("SELECT 1")
