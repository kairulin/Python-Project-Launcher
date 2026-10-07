from PySide6.QtWidgets import (QStackedWidget)

from widgets.command_output import CommandOutput


class ProjectCommandStack(QStackedWidget):
    def __init__(self):
        super().__init__()

        self.project_outputs = {}

        self.empty_page = CommandOutput()

        self.addWidget(self.empty_page)

    def add_project(self, project_directory: str):
        if (project_directory in self.project_outputs):
            return

        command_output = CommandOutput()

        self.project_outputs[project_directory] = command_output

        self.addWidget(command_output)

        # return command_output

    def show_project(self, project_directory: str):
        command_output = self.project_outputs.get(project_directory)
        if command_output is None:
            self.add_project(project_directory)
            command_output = self.project_outputs[project_directory]

        self.setCurrentWidget(command_output)

    def append_output(
        self,
        project_directory: str,
        text: str,
    ):
        command_output = self.project_outputs.get(
            project_directory
        )

        if command_output is None:
            self.add_project(
                project_directory
            )

            command_output = self.project_outputs[
                project_directory
            ]

        command_output.append_output(text)

    def remove_project(self, project_directory: str):
        # 從字典刪除，並回傳對應的 CommandOutput
        command_output = self.project_outputs.pop(
            project_directory,
            None
        )

        if command_output is None:
            return False

        self.removeWidget(command_output)
        command_output.deleteLater()

        return True
