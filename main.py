import sys

from PySide6.QtWidgets import QApplication

from widgets.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)

    app.setStyle("Fusion")  # 設定應用程式的樣式為 Fusion

    window = MainWindow()
    window.show()

    raise SystemExit(app.exec())