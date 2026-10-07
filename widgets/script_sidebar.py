import sys
from PySide6.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QWidget
from PySide6.QtCore import Signal


class ScriptSidebar(QWidget):
    run_script_requested = Signal(str)
    stop_requested = Signal()

    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout(self)

        self.label = QLabel("npm scripts")

        self.stop_button = QPushButton("停止")

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.stop_button)
        self.layout.addStretch()

        self.stop_button.clicked.connect(
            self.stop_requested.emit
        )
        self.stop_button.setEnabled(False)
        # self.stop_button.setStyleSheet("""
        #     QPushButton {
        #         disabled
        #     }

        # """)
        # self.setLayout(layout)

    def set_scripts(self, scripts):
        self.clear_script_buttons()

        if not scripts:
            label = QLabel("沒找到 npm scripts")
            label.setObjectName("script_item")

            self.layout.insertWidget(self.layout.count() - 1, label)
            return

        for script_name, command in scripts.items():
            button = QPushButton(f"npm run {script_name}")
            button.setToolTip(command)
            button.setObjectName("script_item")
            button.clicked.connect(
                lambda checked=False, name=script_name:
                    self.run_script_requested.emit(name)
            )

            self.layout.insertWidget(self.layout.count() - 1, button)

    def clear(self):
        self.clear_script_buttons()

        label = QLabel("請先選擇專案")
        label.setObjectName("script_item")

        self.layout.insertWidget(
            self.layout.count() - 1,
            label
        )

        self.stop_button.setEnabled(False)

    def clear_script_buttons(self):
        for index in reversed(range(self.layout.count())):
            item = self.layout.itemAt(index)
            widget = item.widget()

            if (widget and widget.objectName() == "script_item"):
                self.layout.removeWidget(widget)
                widget.deleteLater()

    def set_stop_enabled(self, enabled: bool):
        self.stop_button.setEnabled(enabled)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ScriptSidebar()
    window.show()
    app.exec()
