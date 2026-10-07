import shutil
import subprocess
from PySide6.QtCore import QProcess, Signal, QObject


class CommandRunner(QObject):
    # (專案路徑, 輸出文字)
    output_received = Signal(str, str)
    command_started = Signal(str, str)
    command_finished = Signal(str, int)
    command_failed = Signal(str, str)

    def __init__(self):
        super().__init__()

        # self.process = QProcess(self)
        self.processes = {}

        # self.process.setProcessChannelMode(
        #     QProcess.ProcessChannelMode.MergedChannels
        # )

        # self.process.readyReadStandardOutput.connect(self.handle_output)

        # self.process.started.connect(self.handle_started)

        # self.process.finished.connect(self.handle_finished)

        # self.process.errorOccurred.connect(self.handle_failed)

    def run_command(self, command, project_directory=None):
        if not project_directory:
            self.command_failed.emit(
                "",
                "專案目錄未設定，請先選擇專案"
            )
            return

        existing_process = self.processes.get(project_directory)

        if (
            existing_process is not None
            and existing_process.state()
            != QProcess.ProcessState.NotRunning
        ):
            self.command_failed.emit(
                project_directory or "",
                "已有指令正在執行中，請稍後再試"
            )
            return

        npm_path = (
            shutil.which("npm") or shutil.which("npm.cmd")
        )

        if not npm_path:
            self.command_failed.emit(
                project_directory,
                "找不到 npm 指令，請確認是否已安裝 Node.js"
            )
            return
        # 1. 建立程序
        process = QProcess(self)
        # 2. 設定輸出通道
        process.setProcessChannelMode(
            QProcess.ProcessChannelMode.MergedChannels
        )
        # self.current_command = command
        # self.current_project_directory = project_directory

        # 3. 設定工作目錄
        process.setWorkingDirectory(project_directory)
        # 4. 設定執行程式和參數
        process.setProgram(npm_path)

        process.setArguments(["run", command])
        # 5. 連接 Signals
        process.readyReadStandardOutput.connect(
            lambda p=process, directory=project_directory: self.handle_output(
                directory, p)
        )

        process.started.connect(
            lambda directory=project_directory,
            script=command:
            self.handle_started(directory, script)
        )

        process.finished.connect(
            lambda exit_code,
            exit_status,
            directory=project_directory,
            p=process:
                self.handle_finished(
                    directory,
                    p,
                    exit_code,
                    exit_status,
                )
        )

        process.errorOccurred.connect(
            lambda error,
            directory=project_directory,
            p=process:
            self.handle_failed(
                directory,
                p,
                error,
            )
        )
        # 6. 保存 Process
        self.processes[
            project_directory
        ] = process
        # 7. 最後才啟動
        process.start()

    def handle_output(self, project_directory: str, process: QProcess):
        output = process.readAllStandardOutput()
        output_text = bytes(output).decode("utf-8", errors="replace")

        if output_text:
            self.output_received.emit(
                project_directory,
                output_text
            )

    def handle_started(self, project_directory: str, command: str):
        message = (
            f"> npm run {command}\n"
            f"專案目錄：{project_directory}\n\n"
        )
        self.command_started.emit(
            project_directory,
            message
        )

    def handle_finished(self, project_directory: str, process: QProcess, exit_code, exit_status):
        # 讀取程序結束前剩餘的輸出
        self.handle_output(
            project_directory,
            process
        )

        stored_process = self.processes.get(project_directory)

        if stored_process is process:
            self.processes.pop(project_directory, None)

        process.deleteLater()

        self.command_finished.emit(
            project_directory,
            exit_code
        )


    def handle_failed(self,  project_directory: str, process: QProcess, error):
        # self.command_failed.emit(str(error))
        self.command_failed.emit(
            project_directory,
            process.errorString()
        )

        if (
            process.state()
            == QProcess.ProcessState.NotRunning
        ):
            self.processes.pop(
                project_directory,
                None,
            )

            process.deleteLater()

    def stop_project(self, project_directory: str):
        process = self.processes.get(project_directory)

        if process is None:
            self.command_failed.emit(
                project_directory,
                "沒有執行中的指令"
            )
            return

        if process.state() == QProcess.ProcessState.NotRunning:
            self.processes.pop(project_directory, None)
            process.deleteLater()
            return

        process_id = process.processId()

        if process_id:
            result = subprocess.run(
                [
                    "taskkill",
                    "/PID",
                    str(process_id),
                    "/T",
                    "/F",
                ],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            if result.returncode != 0:
                self.command_failed.emit(
                    project_directory,
                    result.stderr or "無法停止程序"
                )
        else:
            process.kill()

    def is_running(self, project_directory: str) -> bool:
        process = self.processes.get(project_directory)

        return (
            process is not None
            and process.state()
            != QProcess.ProcessState.NotRunning
        )