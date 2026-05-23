import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from markitdown_gui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("MarkItDown GUI")
    app.setOrganizationName("MarkItDown")
    app.setStyle("Fusion")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
