from typing import Optional

from app.agents.tools.base import BaseTool
from app.agents.tools.calculator import CalculatorTool
from app.agents.tools.web_search import WebSearchTool
from app.agents.tools.file_reader import FileReaderTool
from app.config import settings


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool):
        self._tools[tool.name] = tool

    def get(self, name: str) -> Optional[BaseTool]:
        return self._tools.get(name)

    def list_tools(self) -> list[dict]:
        return [
            {
                "name": t.name,
                "description": t.description,
                "parameters": t.parameters,
            }
            for t in self._tools.values()
        ]

    def to_openai_tools(self) -> list[dict]:
        return [t.to_openai_tool() for t in self._tools.values()]


tool_registry = ToolRegistry()
tool_registry.register(CalculatorTool())
tool_registry.register(WebSearchTool())
tool_registry.register(FileReaderTool(workspace=settings.workspace_dir))
