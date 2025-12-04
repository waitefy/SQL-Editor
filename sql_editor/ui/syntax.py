from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PyQt6.QtCore import QRegularExpression

# Глобальный список ключевых слов (используется и здесь, и в editor.py)
SQL_KEYWORDS = [
    "SELECT", "FROM", "WHERE", "INSERT", "INTO", "VALUES", "UPDATE", "SET",
    "DELETE", "DROP", "CREATE", "TABLE", "INDEX", "ALTER", "VIEW", "AND", "OR",
    "NOT", "NULL", "PRIMARY", "KEY", "FOREIGN", "REFERENCES", "DEFAULT",
    "ORDER", "BY", "GROUP", "LIMIT", "JOIN", "INNER", "LEFT", "RIGHT", "ON",
    "AS", "DISTINCT", "COUNT", "MAX", "MIN", "AVG", "SUM", "LIKE", "IN",
    "IS", "EXISTS", "BETWEEN", "HAVING", "UNION", "ALL"
]


class SqlHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._highlighting_rules = []

        # Устанавливаем тему по умолчанию (темную)
        self.set_theme("dark")

    def set_theme(self, mode="dark"):
        """Перестройка правил подсветки под выбранную тему"""
        self._highlighting_rules = []

        # Настройка палитры
        if mode == "dark":
            colors = {
                "keyword": "#cc7832", # Оранжевый
                "string": "#6a8759",  # Зеленый
                "number": "#6897bb",  # Голубой
                "comment": "#808080"  # Серый
            }
        else:
            colors = {
                "keyword": "#0033b3", # Темно-синий (как в IntelliJ IDEA)
                "string": "#067d17",  # Темно-зеленый
                "number": "#1750eb",  # Ярко-синий
                "comment": "#8c8c8c"  # Серый
            }

        # Создание форматов
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor(colors["keyword"]))
        keyword_format.setFontWeight(QFont.Weight.Bold)

        string_format = QTextCharFormat()
        string_format.setForeground(QColor(colors["string"]))

        number_format = QTextCharFormat()
        number_format.setForeground(QColor(colors["number"]))

        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor(colors["comment"]))

        # Правила
        for word in SQL_KEYWORDS:
            pattern = QRegularExpression(
                rf"\b{word}\b",
                QRegularExpression.PatternOption.CaseInsensitiveOption
            )
            self._highlighting_rules.append((pattern, keyword_format))

        self._highlighting_rules.append((QRegularExpression(r"'.*?'"), string_format))
        self._highlighting_rules.append((QRegularExpression(r'".*?"'), string_format))
        self._highlighting_rules.append((QRegularExpression(r"\b[0-9]+\b"), number_format))
        self._highlighting_rules.append((QRegularExpression(r"--[^\n]*"), comment_format))

        # Принудительно перерисовываем подсветку
        self.rehighlight()

    def highlight_block(self, text):
        for pattern, fmt in self._highlighting_rules:
            iterator = pattern.globalMatch(text)
            while iterator.hasNext():
                match = iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)
