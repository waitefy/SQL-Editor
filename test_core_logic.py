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
        # Для DDL-запросов ожидаем пустые списки
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
        db_manager.execute_query("CREATE TABLE users (id INT, name TEXT)")
        db_manager.execute_query("INSERT INTO users VALUES (1, 'Admin')")

        headers, rows = db_manager.execute_query("SELECT * FROM users")

        assert headers == ['id', 'name']
        assert len(rows) == 1
        assert rows[0][1] == 'Admin'

    def test_get_tables(self, db_manager):
        """Тестирует получение списка таблиц."""
        # 1. Проверяем, что список инициализируется (пустой или с системными таблицами)
        tables = db_manager.get_tables()
        assert isinstance(tables, list)

        # 2. Создаем таблицу
        db_manager.execute_query("CREATE TABLE my_test_table (id INT)")

        # 3. Проверяем, что она появилась в списке
        tables = db_manager.get_tables()
        assert "my_test_table" in tables

    def test_invalid_query(self, db_manager):
        """Тестирует перехват ошибок SQL."""
        with pytest.raises(sqlite3.Error):
            db_manager.execute_query("SELECT * FROM non_existent_table")

    def test_no_connection_error(self):
        """Тестирует попытку запроса без подключения."""
        manager = DatabaseManager()

        # 1. execute_query должен вызвать ошибку
        with pytest.raises(ConnectionError):
            manager.execute_query("SELECT 1")

        # 2. get_tables должен вернуть пустой список (безопасное поведение)
        assert manager.get_tables() == []

    def test_close_connection(self, db_manager):
        """Тестирует закрытие соединения."""
        db_manager.close()
        assert db_manager.connection is None

        # Проверяем защиту от выполнения запросов после закрытия
        with pytest.raises(ConnectionError):
            db_manager.execute_query("SELECT 1")
