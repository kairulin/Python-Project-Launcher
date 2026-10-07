import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication, QHBoxLayout, QMainWindow, QLabel, QFileDialog, QWidget, QVBoxLayout
from widgets.toolbar import ToolBar
from widgets.project_table import ProjectTable
from models.project import Project
from widgets.script_sidebar import ScriptSidebar
from services.project_reader import (read_project_scripts)
from services.command_runner import CommandRunner
from widgets.project_command_stack import ProjectCommandStack
from PySide6.QtCore import QStandardPaths
from services.project_store import ProjectStore


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("專案管理器")
        self.resize(800, 600)

        self.toolbar = ToolBar()
        self.addToolBar(self.toolbar)

        self.toolbar.add_project_requested.connect(
            self.add_project
        )

        self.toolbar.remove_project_requested.connect(
            self.remove_project
        )

        self.toolbar.refresh_requested.connect(
            self.refresh_projects
        )

        self.message_label = QLabel("請選擇操作")
        self.setCentralWidget(self.message_label)

        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        table_layout = QHBoxLayout()

        # 專案表格
        self.project_table = ProjectTable()

        self.project_table.project_selected.connect(
            self.select_project
        )
        # 專案執行按鈕
        self.script_sidebar = ScriptSidebar()

        # 指令輸出區域
        # self.command_output = CommandOutput()
        # layout.addWidget(self.command_output)
        self.command_stack = ProjectCommandStack()

        # 將專案表格、腳本側邊欄和指令輸出區域加入到主佈局中
        table_layout.addWidget(self.project_table)
        table_layout.addWidget(self.script_sidebar)
        layout.addWidget(self.message_label)
        layout.addLayout(table_layout)

        layout.addWidget(self.command_stack)

        self.project_store = ProjectStore()
        self.projects: list[Project] = []

        self.load_saved_projects()

        # 初始化屬性
        self.current_project_directory = None
        self.command_runner = CommandRunner()

        self.script_sidebar.stop_requested.connect(
            self.stop_current_project
        )

        self.script_sidebar.run_script_requested.connect(
            self.run_script
        )

        self.command_runner.output_received.connect(
            self.command_stack.append_output
        )
        self.command_runner.command_started.connect(
            self.on_command_started
        )
        self.command_runner.command_finished.connect(
            self.on_command_finished
        )
        self.command_runner.command_failed.connect(
            self.on_command_failed
        )

        self.setCentralWidget(central_widget)

    def add_project(self):
        desktop_path = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.DesktopLocation
        )
        directory = QFileDialog.getExistingDirectory(
            self, "新增專案", desktop_path)

        if not directory:
            return

        project_name = Path(directory).name
        self.message_label.setText(project_name)

        if any(
            project.directory.casefold()
            == directory.casefold()
            for project in self.projects
        ):
            self.message_label.setText(
                "這專案已存在"
            )
            return

        project = Project(
            name=project_name,
            directory=directory
        )

        self.projects.append(project)

        new_row = self.project_table.insert_project(project)
        self.project_store.save(self.projects)
        self.project_table.selectRow(new_row)

    def remove_project(self):
        directory = self.current_project_directory

        if not directory:
            self.message_label.setText("請先選擇專案")
            return

        if self.command_runner.is_running(directory):
            self.message_label.setText("請先停止正在執行的指令")
            return

        self.projects = [
            project
            for project in self.projects
            if project.directory.casefold()
            != directory.casefold()
        ]
        self.project_table.remove_project(directory)
        self.command_stack.remove_project(directory)

        self.project_store.save(self.projects)

        if self.project_table.rowCount() == 0:
            self.current_project_directory = None
            self.script_sidebar.clear()
            self.script_sidebar.set_stop_enabled(False)

    def refresh_projects(self):
        self.message_label.setText("重新整理")

    def select_project(self, project_directory: str):
        self.current_project_directory = (project_directory)

        self.load_project_scripts(project_directory)
        self.command_stack.show_project(project_directory)

        is_running = self.command_runner.is_running(project_directory)
        self.script_sidebar.set_stop_enabled(is_running)

    def load_project_scripts(self, project_directory: str):
        scripts = read_project_scripts(project_directory)

        self.script_sidebar.set_scripts(scripts)

    def run_script(self, script_name: str):
        if not self.current_project_directory:
            self.command_stack.append_output(
                "",
                "請先選擇專案\n"
            )
            return

        self.command_runner.run_command(
            script_name, self.current_project_directory
        )

    def on_command_finished(self, project_directory: str, exit_code: int):
        target_directory = (
            project_directory
            or self.current_project_directory
        )

        self.command_stack.append_output(
            target_directory,
            f"\n指令結束，exit code:{exit_code}\n"
        )

        self.project_table.update_status(
            project_directory,
            "Ready"
        )

        if self.current_project_directory == project_directory:
            self.script_sidebar.set_stop_enabled(False)

    def on_command_failed(self, project_directory: str, message: str):
        target_directory = (
            project_directory
            or self.current_project_directory
        )

        if not target_directory:
            return

        self.command_stack.append_output(
            target_directory,
            f"\n:{message}\n"
        )

    def on_command_started(self, project_directory: str, message: str):
        self.command_stack.append_output(
            project_directory,
            message
        )

        self.project_table.update_status(
            project_directory,
            "Running"
        )

        if self.current_project_directory == project_directory:
            self.script_sidebar.set_stop_enabled(True)

    def stop_current_project(self):
        project_directory = self.current_project_directory

        if not project_directory:
            return

        self.command_runner.stop_project(
            project_directory
        )

    def load_saved_projects(self):
        self.projects = self.project_store.load()

        for project in self.projects:
            self.project_table.insert_project(project)
            self.command_stack.add_project(project.directory)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    raise SystemExit(app.exec())
