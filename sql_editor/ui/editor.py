from PyQt6.QtWidgets import QPlainTextEdit, QCompleter
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QTextCursor, QKeyEvent, QFont


class CodeEditor(QPlainTextEdit):
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
        # Вычисляем длину того, что мы уже написали (например, "SEL" = 3)
        prefix_len = len(self.completer.completionPrefix())

        # Выделяем это слово влево от курсора
        tc.movePosition(QTextCursor.MoveOperation.Left, QTextCursor.MoveMode.KeepAnchor, prefix_len)

        # Заменяем выделенное на полное слово из словаря
        tc.insertText(completion)
        self.setTextCursor(tc)

    def text_under_cursor(self):
        """Возвращает слово под курсором"""
        tc = self.textCursor()
        tc.select(QTextCursor.SelectionType.WordUnderCursor)
        return tc.selectedText()

    def focusInEvent(self, event):
        if self.completer:
            self.completer.setWidget(self)
        super().focusInEvent(event)

    def keyPressEvent(self, event: QKeyEvent):
        # Если меню открыто, ловим клавиши выбора (Tab, Enter)
        if self.completer and self.completer.popup().isVisible():
            if event.key() in (Qt.Key.Key_Enter, Qt.Key.Key_Return, Qt.Key.Key_Escape, Qt.Key.Key_Tab,
                               Qt.Key.Key_Backtab):
                event.ignore()
                return

        # Проверка на Ctrl+Space (принудительный вызов)
        is_shortcut = (event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_Space)

        # Сначала даем редактору напечатать символ
        if not self.completer or not is_shortcut:
            super().keyPressEvent(event)

        # Не показывать меню при удалении (Backspace/Delete)
        if event.key() in (Qt.Key.Key_Backspace, Qt.Key.Key_Delete):
            if self.completer.popup().isVisible():
                self.completer.popup().hide()
            return

        modifiers = event.modifiers()
        allowed = (modifiers == Qt.KeyboardModifier.NoModifier) or \
                  (modifiers == Qt.KeyboardModifier.ShiftModifier) or \
                  is_shortcut

        if not self.completer or not allowed:
            return

        eow = "~!@#$%^&*()_+{}|:\"<>?,./;'[]\\-="

        completion_prefix = self.text_under_cursor()

        # Не показываем меню, если слово короче 1 символа или ввели спецсимвол
        if not is_shortcut and (len(completion_prefix) < 1 or (event.text() and event.text()[-1] in eow)):
            self.completer.popup().hide()
            return

        # Обновляем список подсказок
        if completion_prefix != self.completer.completionPrefix():
            self.completer.setCompletionPrefix(completion_prefix)
            self.completer.popup().setCurrentIndex(self.completer.completionModel().index(0, 0))

        # Показываем меню
        cr = self.cursorRect()
        cr.setWidth(
            self.completer.popup().sizeHintForColumn(0) + self.completer.popup().verticalScrollBar().sizeHint().width())
        self.completer.complete(cr)
