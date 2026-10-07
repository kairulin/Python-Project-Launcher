import re
import sys
from ansi2html import Ansi2HTMLConverter

from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication, QLabel, QPlainTextEdit, QPushButton, QTextBrowser, QWidget, QVBoxLayout

# from widgets.project_command_stack import ProjectCommandStack
ANSI_SEQUENCE = (
    r"\x1B\[[0-?]*[ -/]*[@-~]"
)

ANSI_PATTERN = re.compile(
    ANSI_SEQUENCE
)

URL_WITH_ANSI_PATTERN = re.compile(
    rf"https?://(?:{ANSI_SEQUENCE}|[^\s\x1B<>])+"
)


class CommandOutput(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        self.label = QLabel("指令輸出")

        # self.output = QPlainTextEdit()
        # self.output.setReadOnly(True)

        self.output = QTextBrowser()
        self.output.setOpenExternalLinks(True)  # 允許點擊外部連結
        self.output.setStyleSheet("""
            QTextBrowser {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #444444;
                font-family: Consolas;
                font-size: 13px;
                padding: 6px;
            }
        """)

        clear_button = QPushButton("清除輸出")
        clear_button.clicked.connect(self.clear_output)

        layout.addWidget(self.label)
        layout.addWidget(self.output)
        layout.addWidget(clear_button)


        self.ansi_converter = Ansi2HTMLConverter(
            inline=True, dark_bg=True, linkify=True)  # 初始化 ANSI 轉換器，啟用 inline 模式和暗色背景

    def append_output(self, text: str):
        text = URL_WITH_ANSI_PATTERN.sub(
            self.clean_url,
            text
        )

        html = self.ansi_converter.convert(
            text, full=False)  # 將 ANSI 文本轉換為 HTML

        html = html.replace("\n", "<br>")  # 將換行符號替換為 <br> 標籤
        cursor = self.output.textCursor()

        cursor.movePosition(QTextCursor.MoveOperation.End)  # 移動到文本末尾
        cursor.insertHtml(html)  # 插入 HTML
        self.output.setTextCursor(cursor)  # 更新 QTextBrowser 的游標位置
        self.output.ensureCursorVisible()

    def clear_output(self):
        self.output.clear()

    def clean_url(self, match):
        return ANSI_PATTERN.sub(
            "",
            match.group(0)
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CommandOutput()
    window.show()
    app.exec()
