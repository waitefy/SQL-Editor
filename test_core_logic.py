import pytest
from sql_editor.db.connection import DatabaseManager


class TestCoreLogic:
    """
    Набор тестов для проверки ядра обработки данных.
    Проверяет класс DatabaseManager без участия GUI.
    """

    @pytest.fixture
    def db_manager(self, tmp_path):
        """Создает временную БД и менеджер соединений."""
        # Используем временную директорию pytest для изоляции тестов
        db_file = tmp_path / "test_core.db"
        manager = DatabaseManager()
        # Метод connect возвращает (success, message)
        success, msg = manager.connect(str(db_file))
        assert success is True
        return manager

    def test_connection_properties(self, db_manager):
        """Тестирует свойства активного соединения."""
        assert db_manager.connection is not None
        assert db_manager.cursor is not None
        # Проверяем, что путь к БД сохранен корректно
        assert db_manager.db_path.endswith("test_core.db")

    def test_create_and_insert(self, db_manager):
        """Тестирует создание таблицы и вставку данных (транзакционность)."""
        # 1. Создание таблицы
        headers, rows, msg = db_manager.execute_query(
            "CREATE TABLE heroes (id INTEGER PRIMARY KEY, name TEXT, power TEXT)"
        )
        # Для DDL-запросов (не SELECT) headers и rows должны быть пустыми списками
        assert headers == []
        assert rows == []
        assert "Операция выполнена успешно" in msg

        # 2. Вставка данных
        headers, rows, msg = db_manager.execute_query(
            "INSERT INTO heroes (name, power) VALUES ('Tony Stark', 'Engineering')"
        )
        assert "Операция выполнена успешно" in msg

    def test_select_data(self, db_manager):
        """Тестирует выборку данных (SELECT)."""
        # Подготовка данных
        db_manager.execute_query("CREATE TABLE users (id INT, name TEXT)")
        db_manager.execute_query("INSERT INTO users VALUES (1, 'Admin')")

        # Выполнение выборки
        headers, rows, msg = db_manager.execute_query("SELECT * FROM users")

        # Проверка структуры ответа
        assert headers == ['id', 'name']  # Проверка заголовков
        assert len(rows) == 1  # Проверка количества строк
        assert rows[0][1] == 'Admin'  # Проверка данных
        assert msg == "Запрос выполнен"

    def test_invalid_query(self, db_manager):
        """Тестирует обработку ошибок SQL."""
        headers, rows, msg = db_manager.execute_query(
            "SELECT * FROM non_existent_table")

        # При ошибке возвращается None
        assert headers is None
        assert rows is None
        assert "SQL Ошибка" in msg

    def test_close_connection(self, db_manager):
        """Тестирует закрытие соединения."""
        db_manager.close()
        # Эмуляция состояния после закрытия для проверки защиты в execute_query
        db_manager.connection = None
        headers, rows, msg = db_manager.execute_query("SELECT 1")
        assert msg == "Нет активного соединения"