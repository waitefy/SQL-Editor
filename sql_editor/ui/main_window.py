import os
import sqlite3
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

        # Логика
        self.db = DatabaseManager()
        self.current_headers = []
        self.current_rows = []

        # Состояние интерфейса (Инициализируем атрибуты здесь)
        self.is_dark_theme = True  # <--- ИСПРАВЛЕНИЕ 2: Перенесено в __init__
        self.highlighter = None
        self.query_editor = None
        self.result_table = None
        self.tree_widget = None

        # Настройки UI
        self.setWindowTitle("SQL Editor")
        self.resize(1200, 800)
        self.settings = QSettings("LinkovSoft", "SQLEditor")

        # Инициализация интерфейса
        self._init_ui()

        # Загрузка состояния (тема, последняя БД)
        self.load_settings()

    def _init_ui(self):
        """Инициализация графических компонентов"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Toolbar
        self.toolbar_layout = QHBoxLayout()
        self.toolbar_layout.setContentsMargins(10, 10, 10, 10)

        self.btn_create = QPushButton("➕ Новая БД")
        self.btn_connect = QPushButton("🔌 Подключить БД")
        self.btn_export = QPushButton("💾 Экспорт")
        self.btn_export.setEnabled(False)
        self.btn_run = QPushButton("▶ Выполнить")
        self.btn_run.setEnabled(False)
        self.btn_theme = QPushButton("🌙️")
        self.btn_theme.setFixedWidth(48)

        self.toolbar_layout.addWidget(self.btn_create)
        self.toolbar_layout.addWidget(self.btn_connect)
        self.toolbar_layout.addWidget(self.btn_export)
        self.toolbar_layout.addWidget(self.btn_run)
        self.toolbar_layout.addStretch()
        self.toolbar_layout.addWidget(self.btn_theme)
        main_layout.addLayout(self.toolbar_layout)

        # Рабочая область
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)

        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabel("База данных")
        self.main_splitter.addWidget(self.tree_widget)

        self.right_splitter = QSplitter(Qt.Orientation.Vertical)

        self.query_editor = CodeEditor()
        completer = QCompleter(SQL_KEYWORDS)
        completer.setModel(QStringListModel(SQL_KEYWORDS))
        self.query_editor.set_completer(completer)
        self.highlighter = SqlHighlighter(self.query_editor.document())

        self.result_table = QTableWidget()
        self.result_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch)
        self.result_table.setSortingEnabled(True)
        self.result_table.verticalHeader().setVisible(False)

        self.right_splitter.addWidget(self.query_editor)
        self.right_splitter.addWidget(self.result_table)
        self.right_splitter.setStretchFactor(0, 1)
        self.right_splitter.setStretchFactor(1, 2)

        self.main_splitter.addWidget(self.right_splitter)
        self.main_splitter.setStretchFactor(0, 1)
        self.main_splitter.setStretchFactor(1, 4)
        main_layout.addWidget(self.main_splitter)

        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Готов к работе")

        # self.is_dark_theme = True — удалено отсюда

        # Сигналы
        self.btn_create.clicked.connect(self.on_create_clicked)
        self.btn_connect.clicked.connect(self.on_connect_clicked)
        self.btn_export.clicked.connect(self.on_export_clicked)
        self.btn_run.clicked.connect(self.on_run_clicked)
        self.btn_theme.clicked.connect(self.toggle_theme)
        self.query_editor.executionRequested.connect(self.on_run_clicked)
        self.tree_widget.itemClicked.connect(self.on_tree_item_clicked)

        self.query_editor.setFocus()
        self.setStyleSheet(DARK_THEME)

    def load_settings(self):
        """Загрузка настроек приложения"""
        saved_theme = self.settings.value("theme", "dark")
        if saved_theme == "light":
            self.toggle_theme()

        last_db_path = self.settings.value("last_db")
        if last_db_path and os.path.exists(last_db_path):
            try:
                self.db.connect(last_db_path)
                self.status_bar.showMessage(
                    f"Восстановлена сессия: {os.path.basename(last_db_path)}")
                self.btn_run.setEnabled(True)
                self.update_tree_structure()
            except (sqlite3.Error,
                    OSError):  # <--- ИСПРАВЛЕНИЕ 1: Ловим только ошибки БД и ОС
                self.settings.remove("last_db")
                self.status_bar.showMessage("Не удалось открыть предыдущую БД")
        else:
            self.settings.remove("last_db")

    def toggle_theme(self):
        if self.is_dark_theme:
            self.setStyleSheet(LIGHT_THEME)
            self.highlighter.set_theme("light")
            self.btn_theme.setText("☀️")
            self.is_dark_theme = False
            self.settings.setValue("theme", "light")
        else:
            self.setStyleSheet(DARK_THEME)
            self.highlighter.set_theme("dark")
            self.btn_theme.setText("🌙")
            self.is_dark_theme = True
            self.settings.setValue("theme", "dark")

    def on_create_clicked(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Создать БД", "", "SQLite Database (*.db *.sqlite)"
        )
        if file_path:
            if not file_path.lower().endswith(('.db', '.sqlite')):
                file_path += '.db'

            try:
                self.db.connect(file_path)
                self.settings.setValue("last_db", file_path)
                self.btn_run.setEnabled(True)
                self.update_tree_structure()
                QMessageBox.information(self, "Успех",
                                        f"БД создана: {file_path}")
            except Exception as e:
                # Здесь Exception допустим для верхнеуровневого перехвата в UI слоте,
                # чтобы приложение не упало при неожиданной ошибке.
                QMessageBox.critical(self, "Ошибка",
                                     f"Не удалось создать БД:\n{e}")

    def on_connect_clicked(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Открыть БД", "",
            "SQLite Database (*.db *.sqlite);;All Files (*)"
        )
        if file_path:
            try:
                self.db.connect(file_path)
                self.status_bar.showMessage(
                    f"Подключено: {os.path.basename(file_path)}")
                self.settings.setValue("last_db", file_path)
                self.btn_run.setEnabled(True)
                self.update_tree_structure()
            except Exception as e:
                self.status_bar.showMessage("Ошибка подключения")
                QMessageBox.critical(self, "Ошибка",
                                     f"Не удалось открыть файл:\n{e}")

    def on_export_clicked(self):
        if not self.current_rows:
            QMessageBox.warning(self, "Ошибка", "Нет данных для экспорта")
            return

        file_path, selected_filter = QFileDialog.getSaveFileName(
            self, "Экспорт данных", "export_data",
            "CSV Files (*.csv);;JSON Files (*.json)"
        )
        if not file_path:
            return

        try:
            if file_path.endswith('.csv') or "CSV" in selected_filter:
                if not file_path.endswith('.csv'): file_path += '.csv'
                export_to_csv(file_path, self.current_headers,
                              self.current_rows)
            else:
                if not file_path.endswith('.json'): file_path += '.json'
                export_to_json(file_path, self.current_headers,
                               self.current_rows)

            QMessageBox.information(self, "Успех", "Файл успешно сохранен")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка экспорта",
                                 f"Не удалось сохранить файл:\n{e}")

    def on_run_clicked(self):
        sql = self.query_editor.toPlainText().strip()
        if not sql:
            QMessageBox.warning(self, "Внимание", "Пустой запрос")
            return

        try:
            # Чистый вызов логики
            headers, rows = self.db.execute_query(sql)

            # Успех
            self.status_bar.showMessage("Запрос выполнен")
            self.fill_table(headers, rows)
            self.update_tree_structure()

            if not headers:  # Если это был не SELECT
                QMessageBox.information(self, "Успех",
                                        "Операция выполнена успешно")

        except sqlite3.Error as e:
            self.status_bar.showMessage("Ошибка SQL")
            QMessageBox.critical(self, "SQL Ошибка",
                                 f"Синтаксическая ошибка или ошибка БД:\n{e}")
        except ConnectionError as e:
            QMessageBox.warning(self, "Ошибка соединения", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Критическая ошибка", str(e))

    def on_tree_item_clicked(self, item):
        if item.parent():
            table_name = item.text(0)
            self.query_editor.setPlainText(f"SELECT * FROM {table_name};")
            self.on_run_clicked()

    def update_tree_structure(self):
        self.tree_widget.clear()
        if not self.db.db_path: return

        db_name = os.path.basename(self.db.db_path)
        root = QTreeWidgetItem(self.tree_widget, [db_name])

        tables = self.db.get_tables()
        for table in tables:
            QTreeWidgetItem(root, [table])
        root.setExpanded(True)

    def fill_table(self, headers, rows):
        self.current_headers = headers
        self.current_rows = rows
        self.btn_export.setEnabled(bool(rows))

        if not headers:
            self.result_table.clear()
            self.result_table.setRowCount(0)
            self.result_table.setColumnCount(0)
            return

        self.result_table.setColumnCount(len(headers))
        self.result_table.setHorizontalHeaderLabels(headers)
        self.result_table.setRowCount(len(rows))

        for r, row_data in enumerate(rows):
            for c, value in enumerate(row_data):
                self.result_table.setItem(r, c, QTableWidgetItem(str(value)))
