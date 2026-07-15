import os

from app.agents.tools.base import BaseTool


class FileReaderTool(BaseTool):
    name = "file_reader"
    description = "Read the contents of a file from the allowed directory."
    parameters = {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Relative file path within the workspace",
            }
        },
        "required": ["path"],
    }

    def __init__(self, workspace: str = "."):
        self.workspace = os.path.abspath(workspace)

    async def run(self, path: str) -> str:
        full_path = os.path.abspath(os.path.join(self.workspace, path))
        if not full_path.startswith(self.workspace):
            return "Error: Access denied. Path is outside workspace."
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read(4096)
            return content
        except FileNotFoundError:
            return f"Error: File not found: {path}"
        except Exception as e:
            return f"Error reading file: {e}"
