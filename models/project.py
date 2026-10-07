from dataclasses import dataclass

@dataclass
class Project:
    name: str
    directory: str
    required_node: str = "Unknown"
    runtime_node: str = "尚未執行"
    status: str = "Ready"