import sys
from PySide6.QtWidgets import QApplication, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
from PySide6.QtCore import Signal
from models.project import Project


class ProjectTable(QTableWidget):
    project_selected = Signal(str)

    def __init__(self):
        super().__init__(0, 5)

        self.setHorizontalHeaderLabels(
            ['專案名稱', 'Node 版本', '執行版本', '狀態', '路徑'])

        header = self.horizontalHeader()

        for column in range(4):
            header.setSectionResizeMode(
                column,
                QHeaderView.ResizeMode.ResizeToContents)

        header.setSectionResizeMode(
            4,
            QHeaderView.ResizeMode.Stretch)

        # 點擊任意格子選取整列
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        # 一次只能一列
        self.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)

        # 禁止修改內容
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        self.itemSelectionChanged.connect(
            self.on_selection_changed
        )
        # self.cellClicked.connect(
        #     self.on_cell_clicked
        # )

        # self.setStyleSheet("""
        #     QTableWidget {
        #         border: none;
        #         gridline-color: #454545;
        #     }

        #     QTableWidget::item {
        #         padding: 4px;
        #     }

        #     QTableWidget::item:selected {
        #         background-color: #0d6efd;
        #         color: white;
        #     }

        #     QTableWidget::item:focus {
        #         border: none;
        #     }

        #     QHeaderView::section {
        #         padding: 5px;
        #         font-weight: 600;
        #     }
        # """)
        # self.insert_row()

        # self.setItem(count, 0, QTableWidgetItem("Project Launcher"))
        # self.setItem(count, 1, QTableWidgetItem("20.10.0"))
        # self.setItem(count, 2, QTableWidgetItem("v20.10.0"))
        # self.setItem(count, 3, QTableWidgetItem("Ready"))
        # self.setItem(count, 4, QTableWidgetItem(
        #     "C:/Projects/Project Launcher"))

    def insert_project(self, project: Project):
        row = self.rowCount()
        self.insertRow(row)

        self.set_project(row, project)
        return row

    def remove_project(self, project_directory: str):
        for row in range(self.rowCount()):
            item = self.item(row, 4)

            if item is not None and item.text() == project_directory:
                self.removeRow(row)
                return

    def set_project(self, row, project: Project):
        values = [
            project.name,
            project.required_node,
            project.runtime_node,
            project.status,
            project.directory
        ]

        for column, value in enumerate(values):
            self.setItem(
                row,
                column,
                QTableWidgetItem(value),
            )

        # self.setItem(row, 0, QTableWidgetItem(project_name))
        # self.setItem(row, 4, QTableWidgetItem(
        #     directory))

    # def on_cell_clicked(self,
    #                     row: int,
    #                     column: int
    #                     ):
    #     path_item = self.item(row, 4)

    #     if path_item is None:
    #         return

    #     project_directory = path_item.text()
    #     self.project_selected.emit(project_directory)
    def on_selection_changed(self):
        row = self.currentRow()
        if row < 0:
            return

        path_item = self.item(row, 4)

        if path_item is None:
            return

        project_directory = path_item.text()
        self.project_selected.emit(project_directory)

    def update_status(self, project_directory: str, status: str):
        for row in range(self.rowCount()):
            path_item = self.item(row, 4)

            if (path_item is not None and path_item.text() == project_directory):
                status_item = self.item(row, 3)

                if status_item is None:
                    self.setItem(
                        row,
                        3,
                        QTableWidgetItem(status)
                    )
                else:
                    status_item.setText(status)

                return


if __name__ == "__main__":
    app = QApplication(sys.argv)
    table = ProjectTable()
    table.resize(800, 400)
    table.show()

    raise SystemExit(app.exec())
