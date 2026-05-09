import sys

from PySide6.QtWidgets import QApplication
from src.ui.main_window import MainWindow

VERSION = "1.0.2"


def main():
    app = QApplication(sys.argv)
    window = MainWindow(VERSION)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
