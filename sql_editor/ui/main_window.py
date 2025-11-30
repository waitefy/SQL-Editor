import os
from PyQt6.QtWidgets import (
    QCompleter, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QPushButton, QTableWidget, QTreeWidget,
    QSplitter, QHeaderView, QTreeWidgetItem,
    QMessageBox, QFileDialog, QTableWidgetItem
)
from PyQt6.QtCore import Qt, QStringListModel, QSettings
from sql_editor.db.connection import DatabaseManager
from sql_editor.ui.syntax import SqlHighlighter, SQL_KEYWORDS
from sql_editor.ui.editor import CodeEditor
from sql_editor.utils.export import export_to_csv, export_to_json
from sql_editor.ui.styles import DARK_THEME, LIGHT_THEME


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Создаем экземпляр менеджера БД
        self.db = DatabaseManager()
        self.current_headers = []
        self.current_rows = []
        self.setWindowTitle("SQL Editor")
        self.resize(1200, 800)

        # Основной виджет и layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Переменная состояния темы
        self.is_dark_theme = True

        # Верхняя панель (Toolbar)
        self.toolbar_layout = QHBoxLayout()
        self.toolbar_layout.setContentsMargins(10, 10, 10, 10)
        self.btn_create = QPushButton("➕ Новая БД")
        self.btn_connect = QPushButton("🔌 Подключить БД")
        self.btn_export = QPushButton("💾 Экспорт")
        self.btn_export.setEnabled(False)
        self.btn_run = QPushButton("▶ Выполнить")
        self.btn_run.setEnabled(False)
        self.btn_theme = QPushButton("🌙️")
        self.btn_theme.setToolTip("Сменить тему")
        self.btn_theme.setFixedWidth(48)

        # Добавляем кнопки
        self.toolbar_layout.addWidget(self.btn_create)
        self.toolbar_layout.addWidget(self.btn_connect)
        self.toolbar_layout.addWidget(self.btn_export)
        self.toolbar_layout.addWidget(self.btn_run)
        self.toolbar_layout.addStretch()
        self.toolbar_layout.addWidget(self.btn_theme)
        main_layout.addLayout(self.toolbar_layout)

        # Рабочая область (Сплиттер: Слева дерево, Справа редактор+таблица)
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)

        # --- Левая панель (Дерево БД) ---
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabel("База данных")
        self.main_splitter.addWidget(self.tree_widget)

        # --- Правая панель (Сплиттер: Редактор сверху, Таблица снизу) ---
        self.right_splitter = QSplitter(Qt.Orientation.Vertical)

        # Редактор SQL (Кастомный виджет)
        self.query_editor = CodeEditor()

        # Настройка автодополнения
        completer = QCompleter(SQL_KEYWORDS)
        completer.setModel(QStringListModel(SQL_KEYWORDS))
        self.query_editor.set_completer(completer)

        # Подключаем подсветку синтаксиса
        self.highlighter = SqlHighlighter(self.query_editor.document())

        # --- Таблица результатов ---
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(0)
        self.result_table.setRowCount(0)
        # Растягивать заголовки под ширину
        self.result_table.horizontalHeader()\
            .setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        # Убираем номера строк слева (для красоты)
        self.result_table.verticalHeader().setVisible(False)

        self.right_splitter.addWidget(self.query_editor)
        self.right_splitter.addWidget(self.result_table)

        # Настройка размеров сплиттеров (пропорции)
        self.right_splitter.setStretchFactor(0, 1)  # Редактор
        self.right_splitter.setStretchFactor(1, 2)  # Таблица
        self.main_splitter.addWidget(self.right_splitter)
        self.main_splitter.setStretchFactor(0, 1)  # Дерево
        self.main_splitter.setStretchFactor(1, 4)  # Правая часть
        main_layout.addWidget(self.main_splitter)

        # Статус бар
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Готов к работе")

        # Подключаем сигналы
        self.btn_create.clicked.connect(self.on_create_clicked)
        self.btn_connect.clicked.connect(self.on_connect_clicked)
        self.btn_export.clicked.connect(self.on_export_clicked)
        self.btn_run.clicked.connect(self.on_run_clicked)
        self.btn_theme.clicked.connect(self.toggle_theme)

        # Подключаем Enter в редакторе к выполнению запроса
        self.query_editor.executionRequested.connect(self.on_run_clicked)

        # Обработка клика по таблице в дереве
        self.tree_widget.itemClicked.connect(self.on_tree_item_clicked)

        # Устанавливаем фокус на редактор при запуске
        self.query_editor.setFocus()

        # Применяем стартовую тему
        self.setStyleSheet(DARK_THEME)

        self.settings = QSettings("LinkovSoft", "SQLEditor")

        # Загружаем сохраненное состояние
        self.load_settings()

    def load_settings(self):
        """Загрузка настроек приложения"""
        # 1. Восстановление темы
        saved_theme = self.settings.value("theme", "dark")
        # По умолчанию у нас dark. Если сохранено light - переключаем.
        if saved_theme == "light":
            self.toggle_theme()

        # 2. Восстановление последней БД
        last_db_path = self.settings.value("last_db")

        if last_db_path:
            # Проверяем, существует ли файл (вдруг его удалили)
            if os.path.exists(last_db_path):
                success, message = self.db.connect(last_db_path)
                if success:
                    self.status_bar.showMessage(
                        f"Восстановлена сессия: {message}")
                    self.btn_run.setEnabled(True)
                    self.update_tree_structure()
            else:
                # Если файла нет, удаляем запись из настроек
                self.settings.remove("last_db")
                self.status_bar.showMessage("Предыдущая БД не найдена")

    def toggle_theme(self):
        """Переключение между светлой и темной темой"""
        if self.is_dark_theme:
            # Переключаем на СВЕТЛУЮ
            self.setStyleSheet(LIGHT_THEME)
            self.highlighter.set_theme("light")
            self.btn_theme.setText("☀️")
            self.is_dark_theme = False
            self.settings.setValue("theme", "light")
        else:
            # Переключаем на ТЕМНУЮ
            self.setStyleSheet(DARK_THEME)
            self.highlighter.set_theme("dark")
            self.btn_theme.setText("🌙")
            self.is_dark_theme = True
            self.settings.setValue("theme", "dark")

    def on_create_clicked(self):
        # Диалог СОХРАНЕНИЯ файла (создания нового)
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Создать новую базу данных",
            "",
            "SQLite Database (*.db *.sqlite *.sqlite3 *.db3);;All Files (*)"
        )

        if file_path:
            # Проверяем, есть ли уже у файла одно из допустимых расширений
            valid_extensions = ('.db', '.sqlite', '.sqlite3', '.db3')

            # Если расширения нет, добавляем .db по умолчанию
            if not file_path.lower().endswith(valid_extensions):
                file_path += '.db'

            # Используем тот же метод connect, он создаст файл
            success, message = self.db.connect(file_path)
            self.status_bar.showMessage(message)

            if success:
                self.settings.setValue("last_db", file_path)
                self.btn_run.setEnabled(True)
                self.update_tree_structure()
                QMessageBox.information(
                    self,
                    "Успех",
                    f"База данных успешно создана:\n{file_path}"
                )
            else:
                QMessageBox.critical(self, "Ошибка", message)

    # --- Слоты (Методы обработки событий) ---
    def on_connect_clicked(self):
        # Открываем диалог выбора файла
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Открыть базу данных",
            "",
            "SQLite Database (*.db *.sqlite);;All Files (*)"
        )

        if file_path:
            success, message = self.db.connect(file_path)
            self.status_bar.showMessage(message)

            if success:
                self.settings.setValue("last_db", file_path)
                self.btn_run.setEnabled(True)
                self.update_tree_structure()
            else:
                QMessageBox.critical(self, "Ошибка", message)

    def on_export_clicked(self):
        if not self.current_rows:
            QMessageBox.warning(self, "Ошибка", "Нет данных для экспорта")
            return

        # Диалог сохранения файла
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Экспорт данных",
            "export_data",  # Имя по умолчанию
            "CSV Files (*.csv);;JSON Files (*.json)"
        )

        if not file_path:
            return

        success = False
        message = ""

        # Определяем формат по расширению или фильтру
        if file_path.endswith('.csv') or "CSV" in selected_filter:
            # Если пользователь не написал расширение, добавим его
            if not file_path.endswith('.csv'):
                file_path += '.csv'
            success, message = export_to_csv(
                file_path,
                self.current_headers,
                self.current_rows
            )

        elif file_path.endswith('.json') or "JSON" in selected_filter:
            if not file_path.endswith('.json'):
                file_path += '.json'
            success, message = export_to_json(
                file_path,
                self.current_headers,
                self.current_rows
            )

        if success:
            QMessageBox.information(self, "Успех", message)
        else:
            QMessageBox.critical(self, "Ошибка", message)

    def on_run_clicked(self):
        sql = self.query_editor.toPlainText().strip()
        if not sql:
            QMessageBox.warning(self, "Ошибка", "Введите SQL запрос!")
            return

        # Выполняем запрос
        headers, rows, message = self.db.execute_query(sql)

        if headers is None and rows is None:
            # Ошибка (красное окно)
            self.status_bar.showMessage("Ошибка выполнения")
            QMessageBox.critical(self, "SQL Ошибка", message)
        else:
            # Успех
            self.status_bar.showMessage(message)
            self.fill_table(headers, rows)
            self.update_tree_structure()
            if not headers:
                QMessageBox.information(self, "Успех", message)

    def on_tree_item_clicked(self, item):
        """Обработка клика по элементу дерева (таблице)"""
        # Проверяем, что кликнули по таблице (у неё должен быть родитель)
        if item.parent():
            table_name = item.text(0)

            # Формируем запрос для выборки всех данных
            query = f"SELECT * FROM {table_name};"

            # Вставляем запрос в редактор
            self.query_editor.setPlainText(query)

            # Автоматически выполняем его, как будто нажали кнопку Run
            self.on_run_clicked()

    # --- Вспомогательные методы UI ---
    def update_tree_structure(self):
        """Обновляет дерево таблиц слева"""
        self.tree_widget.clear()

        # Корневой элемент - имя файла
        db_name = self.db.db_path.split("/")[-1]
        root = QTreeWidgetItem(self.tree_widget, [db_name])
        root.setIcon(
            0,
            self.style().standardIcon(
                self.style().StandardPixmap.SP_DriveHDIcon
            )
        )

        # Получаем таблицы
        tables = self.db.get_tables()
        for table in tables:
            QTreeWidgetItem(root, [table])
            # Можно добавить иконку таблицы, если захочется

        root.setExpanded(True)

    def fill_table(self, headers, rows):
        """Заполняет таблицу результатов"""
        # --- СОХРАНЯЕМ ДАННЫЕ ДЛЯ ЭКСПОРТА ---
        self.current_headers = headers
        self.current_rows = rows

        # Разблокируем кнопку экспорта, если есть данные
        if rows:
            self.btn_export.setEnabled(True)
        else:
            self.btn_export.setEnabled(False)

        # Если запрос не вернул данных (например INSERT), очищаем таблицу
        if not headers:
            self.result_table.clear()
            self.result_table.setRowCount(0)
            self.result_table.setColumnCount(0)
            return

        # Настраиваем колонки
        self.result_table.setColumnCount(len(headers))
        self.result_table.setHorizontalHeaderLabels(headers)

        # Настраиваем строки
        self.result_table.setRowCount(len(rows))

        # Заполняем ячейки
        for row_idx, row_data in enumerate(rows):
            for col_idx, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                self.result_table.setItem(row_idx, col_idx, item)
