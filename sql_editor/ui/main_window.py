from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QPlainTextEdit, QTableWidget, QTreeWidget,
    QSplitter, QHeaderView, QTreeWidgetItem, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

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
        self.toolbar_layout.setSpacing(10)

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

        # Редактор SQL
        self.query_editor = QPlainTextEdit()
        self.query_editor.setPlaceholderText("Введите ваш SQL запрос здесь...")
        font = QFont("Courier New", 12)  # Моноширинный шрифт для кода
        self.query_editor.setFont(font)

        # Таблица результатов
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(0)
        self.result_table.setRowCount(0)
        # Растягивать заголовки под ширину
        self.result_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

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

        # Подключаем сигналы (заглушки)
        self.btn_connect.clicked.connect(self.on_connect_clicked)
        self.btn_run.clicked.connect(self.on_run_clicked)

    def _apply_styles(self):
        """Применяем CSS-подобные стили для интерфейса"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
            }
            QWidget {
                color: #e0e0e0; /* Чуть более мягкий белый для текста */
                font-family: 'Segoe UI', sans-serif;
                font-size: 14px;
            }

            /* --- Стили Кнопок (Прозрачные) --- */
            QPushButton {
                background-color: transparent;       /* Прозрачный фон */
                border: 1px solid transparent;       /* Прозрачная рамка (чтобы не прыгало при наведении) */
                padding: 8px 16px;
                border-radius: 6px;                  /* Скругленные углы */
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1); /* Легкая подсветка при наведении (10% белого) */
                border: 1px solid #555;              /* Рамка появляется при наведении */
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.05); /* Чуть темнее при нажатии */
            }
            QPushButton:disabled {
                color: #666666;                      /* Серый текст для неактивных кнопок */
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
            QSplitter::handle {
                background-color: #3c3f41;
                height: 2px;
                width: 2px;
            }
        """)

    # --- Слоты (Методы обработки событий) ---
    def on_connect_clicked(self):
        QMessageBox.information(self, "Подключение", "Здесь будет диалог открытия файла БД")
        # Временная эмуляция успешного подключения
        self.btn_run.setEnabled(True)
        self.status_bar.showMessage("Подключено к example.db")

        # Добавим фейковые данные в дерево для наглядности
        self.tree_widget.clear()
        root = QTreeWidgetItem(self.tree_widget, ["example.db"])
        table1 = QTreeWidgetItem(root, ["users"])
        table2 = QTreeWidgetItem(root, ["orders"])
        root.setExpanded(True)

    def on_run_clicked(self):
        sql = self.query_editor.toPlainText()
        if not sql.strip():
            QMessageBox.warning(self, "Ошибка", "Введите SQL запрос!")
            return

        QMessageBox.information(self, "Выполнение", f"Выполняем запрос:\n{sql}")
        self.status_bar.showMessage("Запрос выполнен успешно")