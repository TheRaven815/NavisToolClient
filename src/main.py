import sys
import os

# Get the project root directory
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from PySide6.QtWidgets import QApplication
from src.ui.main_window import MainWindow

VERSION = "1.0.1"

def main():
    app = QApplication(sys.argv)
    window = MainWindow(VERSION)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
