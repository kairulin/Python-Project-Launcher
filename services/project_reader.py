import json
from pathlib import Path


def read_project_scripts(directory: str) -> dict[str, str]:
    """
    讀取專案的 scripts.json 檔案，並返回一個字典，包含 script 名稱和對應的命令。

    :param directory: 專案目錄的路徑
    :return: 包含 script 名稱和命令的字典
    """
    scripts_file = Path(directory) / "package.json"
    if not scripts_file.exists():
        return {}

    with open(scripts_file, "r", encoding="utf-8") as f:
        try:
            scripts_data = json.load(f)
            return scripts_data.get("scripts", {})
        except json.JSONDecodeError:
            return {}
