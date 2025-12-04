from PyQt6.QtWidgets import QPlainTextEdit, QCompleter
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QTextCursor, QKeyEvent, QFont


class CodeEditor(QPlainTextEdit):
    # Сигнал, который будет испускаться при нажатии Enter
    executionRequested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.completer = None

        # Настройка внешнего вида
        self.setPlaceholderText("Введите ваш SQL запрос здесь...")
        font = QFont("Courier New", 12)
        self.setFont(font)

    def set_completer(self, completer: QCompleter):
        """Установка объекта автодополнения"""
        if self.completer:
            self.completer.activated.disconnect()

        self.completer = completer
        if not self.completer:
            return

        self.completer.setWidget(self)
        self.completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)

        # Подключаем сигнал выбора слова
        self.completer.activated.connect(self.insert_completion)

    def insert_completion(self, completion: str):
        """Вставка выбранного слова с заменой введенного префикса"""
        if self.completer.widget() != self:
            return

        tc = self.textCursor()
        prefix_len = len(self.completer.completionPrefix())
        tc.movePosition(
            QTextCursor.MoveOperation.Left,
            QTextCursor.MoveMode.KeepAnchor,
            prefix_len
        )
        tc.insertText(completion)
        self.setTextCursor(tc)

    def text_under_cursor(self):
        tc = self.textCursor()
        tc.select(QTextCursor.SelectionType.WordUnderCursor)
        return tc.selectedText()

    def focusInEvent(self, event):
        if self.completer:
            self.completer.setWidget(self)
        super().focusInEvent(event)

    def keyPressEvent(self, event: QKeyEvent):
        # Если открыто меню автодополнения — Enter выбирает пункт
        if self.completer and self.completer.popup().isVisible():
            if event.key() in (Qt.Key.Key_Enter, Qt.Key.Key_Return,
                               Qt.Key.Key_Escape, Qt.Key.Key_Tab,
                               Qt.Key.Key_Backtab):
                event.ignore()
                return

        # Обработка Enter (Запуск) vs Shift+Enter (Новая строка)
        if event.key() in (Qt.Key.Key_Enter, Qt.Key.Key_Return):
            # Если нажат Shift -> Обычный перенос строки
            if event.modifiers() == Qt.KeyboardModifier.ShiftModifier:
                super().keyPressEvent(event)
                return

            # Если просто Enter - Выполняем запрос
            if event.modifiers() == Qt.KeyboardModifier.NoModifier:
                self.executionRequested.emit()
                return

        # Принудительный вызов автодополнения через Ctrl+Space
        is_shortcut = (event.modifiers() == Qt.KeyboardModifier.ControlModifier
                       and event.key() == Qt.Key.Key_Space)

        # Сначала даем редактору обработать ввод символа
        if not self.completer or not is_shortcut:
            super().keyPressEvent(event)

        # Логика автодополнения

        # Не показывать меню при удалении
        if event.key() in (Qt.Key.Key_Backspace, Qt.Key.Key_Delete):
            if self.completer.popup().isVisible():
                self.completer.popup().hide()
            return

        # Разрешаем работу с Shift (заглавные буквы) и без модификаторов
        modifiers = event.modifiers()
        allowed = (modifiers == Qt.KeyboardModifier.NoModifier) or \
                  (modifiers == Qt.KeyboardModifier.ShiftModifier) or \
                  is_shortcut

        if not self.completer or not allowed:
            return

        eow = "~!@#$%^&*()_+{}|:\"<>?,./;'[]\\-="
        completion_prefix = self.text_under_cursor()

        if not is_shortcut and (len(completion_prefix) < 1
                                or (event.text() and event.text()[-1] in eow)):
            self.completer.popup().hide()
            return

        if completion_prefix != self.completer.completionPrefix():
            self.completer.setCompletionPrefix(completion_prefix)
            self.completer.popup()\
                .setCurrentIndex(self.completer.completionModel().index(0, 0))

        cr = self.cursorRect()
        cr.setWidth(
            self.completer.popup().sizeHintForColumn(0) +
            self.completer.popup().verticalScrollBar().sizeHint().width())
        self.completer.complete(cr)
