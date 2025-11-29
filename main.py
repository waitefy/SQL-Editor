import sys
from PyQt6.QtWidgets import QApplication
from sql_editor.ui.main_window import MainWindow


def main():
    # Создаем экземпляр приложения
    app = QApplication(sys.argv)

    # Создаем и показываем главное окно
    window = MainWindow()
    window.show()

    # Запускаем цикл событий
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
