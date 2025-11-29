from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PyQt6.QtCore import QRegularExpression

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

        # --- Форматы стилей ---
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#cc7832"))
        keyword_format.setFontWeight(QFont.Weight.Bold)

        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#6a8759"))

        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#6897bb"))

        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#808080"))

        # --- Правила ---

        # 1. Ключевые слова (используем глобальный список)
        for word in SQL_KEYWORDS:
            pattern = QRegularExpression(rf"\b{word}\b", QRegularExpression.PatternOption.CaseInsensitiveOption)
            self._highlighting_rules.append((pattern, keyword_format))

        # 2. Строки
        self._highlighting_rules.append((QRegularExpression(r"'.*?'"), string_format))
        self._highlighting_rules.append((QRegularExpression(r'".*?"'), string_format))

        # 3. Числа
        self._highlighting_rules.append((QRegularExpression(r"\b[0-9]+\b"), number_format))

        # 4. Комментарии
        self._highlighting_rules.append((QRegularExpression(r"--[^\n]*"), comment_format))

    def highlightBlock(self, text):
        for pattern, fmt in self._highlighting_rules:
            iterator = pattern.globalMatch(text)
            while iterator.hasNext():
                match = iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)
