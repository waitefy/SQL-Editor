from PyQt6.QtWidgets import (
    QCompleter, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTreeWidget,
    QSplitter, QHeaderView, QTreeWidgetItem, QMessageBox, QFileDialog, QTableWidgetItem
)
from PyQt6.QtCore import Qt, QStringListModel
from sql_editor.db.connection import DatabaseManager
from sql_editor.ui.syntax import SqlHighlighter, SQL_KEYWORDS
from sql_editor.ui.editor import CodeEditor

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Создаем экземпляр менеджера БД
        self.db = DatabaseManager()

        self.setWindowTitle("SQL Editor")
        self.resize(1200, 800)

        # Основной виджет и layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Верхняя панель (Toolbar)
        self.toolbar_layout = QHBoxLayout()
        self.toolbar_layout.setContentsMargins(10, 10, 10, 10)

        self.btn_connect = QPushButton("🔌 Подключить БД")
        self.btn_run = QPushButton("▶ Выполнить")
        self.btn_run.setEnabled(False)  # Пока нет соединения

        # Добавляем кнопки и растягивающийся разделитель
        self.toolbar_layout.addWidget(self.btn_connect)
        self.toolbar_layout.addWidget(self.btn_run)
        self.toolbar_layout.addStretch()

        main_layout.addLayout(self.toolbar_layout)

        # 2. Рабочая область (Сплиттер: Слева дерево, Справа редактор+таблица)
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

        # Таблица результатов
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(0)
        self.result_table.setRowCount(0)
        # Растягивать заголовки под ширину
        self.result_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
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

        # 3. Статус бар
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Готов к работе")

        # Применяем стили (Темная тема)
        self._apply_styles()

        # Подключаем сигналы
        self.btn_connect.clicked.connect(self.on_connect_clicked)
        self.btn_run.clicked.connect(self.on_run_clicked)

    def _apply_styles(self):
        """Применяем CSS-подобные стили для интерфейса"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
            }
            QWidget {
                color: #e0e0e0;
                font-family: 'Segoe UI', sans-serif;
                font-size: 14px;
            }

            /* --- Стили Кнопок (Прозрачные) --- */
            QPushButton {
                background-color: transparent;
                border: 1px solid transparent;
                padding: 8px 16px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
                border: 1px solid #555;
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.05);
            }
            QPushButton:disabled {
                color: #666666;
            }

            /* --- Остальные элементы --- */
            QTreeWidget, QTableWidget, QPlainTextEdit {
                background-color: #1e1e1e;
                border: 1px solid #3c3f41;
                color: #dcdcdc;
                border-radius: 4px;
            }
            QHeaderView::section {
                background-color: #2b2b2b;
                padding: 4px;
                border: none;
                border-bottom: 2px solid #3c3f41;
            }
            QTableCornerButton::section {
                background-color: #2b2b2b;
                border: none;
            }
            QSplitter::handle {
                background-color: #3c3f41;
                height: 2px;
                width: 2px;
            }
        """)

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
                self.btn_run.setEnabled(True)
                self.update_tree_structure()
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
            # Ошибка
            self.status_bar.showMessage("Ошибка выполнения")
            QMessageBox.critical(self, "SQL Ошибка", message)
        else:
            # Успех
            self.status_bar.showMessage(message)
            self.fill_table(headers, rows)

            # Обновляем дерево таблиц, чтобы увидеть изменения (CREATE/DROP)
            self.update_tree_structure()

    # --- Вспомогательные методы UI ---
    def update_tree_structure(self):
        """Обновляет дерево таблиц слева"""
        self.tree_widget.clear()

        # Корневой элемент - имя файла
        db_name = self.db.db_path.split("/")[-1]
        root = QTreeWidgetItem(self.tree_widget, [db_name])
        root.setIcon(0, self.style().standardIcon(self.style().StandardPixmap.SP_DriveHDIcon))

        # Получаем таблицы
        tables = self.db.get_tables()
        for table in tables:
            QTreeWidgetItem(root, [table])
            # Можно добавить иконку таблицы, если захочется

        root.setExpanded(True)

    def fill_table(self, headers, rows):
        """Заполняет таблицу результатов"""
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
