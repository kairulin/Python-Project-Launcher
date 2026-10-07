import sys
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QApplication, QToolBar
from PySide6.QtGui import QAction


class ToolBar(QToolBar):
    add_project_requested = Signal()
    remove_project_requested = Signal()
    refresh_requested = Signal()

    def __init__(self):
        super().__init__("工具欄")

        self.setMovable(False)

        add_project_action = QAction("新增專案", self)
        remove_project_action = QAction("移除專案", self)
        refresh_action = QAction("重新整理", self)

        add_project_action.triggered.connect(
            lambda: self.add_project_requested.emit()
        )

        remove_project_action.triggered.connect(
            lambda: self.remove_project_requested.emit()
        )

        refresh_action.triggered.connect(
            lambda: self.refresh_requested.emit()
        )

        self.addAction(add_project_action)
        self.addAction(remove_project_action)
        # 分隔線
        self.addSeparator()
        self.addAction(refresh_action)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    toolbar = ToolBar()
    toolbar.show()

    raise SystemExit(app.exec())
