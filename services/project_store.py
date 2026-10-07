import json
import os
from pathlib import Path

from models.project import Project

class ProjectStore:
    def __init__(self):
        app_data = os.getenv("APPDATA") or str(Path.home())

        self.file_path = (
            Path(app_data)
            / "LearnProjectLauncher"
            /"projects.json"
        )

    def save(self, projects: list[Project]):
        self.file_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        data = [
            {
                "name": project.name,
                "directory": project.directory
            }
            for project in projects
        ]

        self.file_path.write_text(
            json.dumps(
                data,
                ensure_ascii=False,
                indent=2
            ),
            encoding="utf-8"
        )

    def load(self) -> list[Project]:
        if not self.file_path.exists():
            return []

        try:
            data = json.loads(
                self.file_path.read_text(
                    encoding="utf-8"
                )
            )

            return [
                Project(
                    name=item["name"],
                    directory=item["directory"]
                )
                for item in data
                if "name" in item and "directory" in item
            ]

        except (
            OSError,
            json.JSONDecodeError,
            TypeError,
            KeyError
        ):
            return []
