DARK_THEME = """
QMainWindow {
    background-color: #2b2b2b;
}
QWidget {
    color: #e0e0e0;
    font-family: 'Segoe UI', sans-serif;
    font-size: 14px;
}
/* Кнопки */
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
/* Элементы ввода и таблицы */
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
/* Меню автодополнения */
QListView {
    background-color: #2b2b2b;
    color: #dcdcdc;
    border: 1px solid #555;
}
"""

LIGHT_THEME = """
QMainWindow {
    background-color: #f5f5f5;
}
QWidget {
    color: #333333;
    font-family: 'Segoe UI', sans-serif;
    font-size: 14px;
}
/* Кнопки */
QPushButton {
    background-color: transparent;
    border: 1px solid transparent;
    padding: 8px 16px;
    border-radius: 6px;
}
QPushButton:hover {
    background-color: rgba(0, 0, 0, 0.05);
    border: 1px solid #ccc;
}
QPushButton:pressed {
    background-color: rgba(0, 0, 0, 0.1);
}
QPushButton:disabled {
    color: #a0a0a0;
}
/* Элементы ввода и таблицы */
QTreeWidget, QTableWidget, QPlainTextEdit {
    background-color: #ffffff;
    border: 1px solid #c0c0c0;
    color: #333333;
    border-radius: 4px;
}
QHeaderView::section {
    background-color: #e0e0e0;
    padding: 4px;
    border: none;
    border-bottom: 1px solid #c0c0c0;
}
QTableCornerButton::section {
    background-color: #e0e0e0;
    border: none;
}
QSplitter::handle {
    background-color: #c0c0c0;
    height: 2px;
    width: 2px;
}
QListView {
    background-color: #ffffff;
    color: #333333;
    border: 1px solid #ccc;
}
"""
