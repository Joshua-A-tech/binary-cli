from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass
class Tool:
    name: str
    description: str
    parameters: dict[str, Any]
    func: Callable[..., Any]

    def execute(self, **kwargs) -> str:
        try:
            result = self.func(**kwargs)
            return str(result)
        except Exception as exc:  # noqa: BLE001
            return f"Error executing {self.name}: {exc}"

    def to_gemini_schema(self) -> dict[str, Any]:
        """Convert standard parameters dict into Gemini function declaration format."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
        }


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool | None:
        return self._tools.get(name)

    def list_tools(self) -> list[Tool]:
        return list(self._tools.values())

    def execute(self, name: str, **kwargs) -> str:
        tool = self.get(name)
        if not tool:
            return f"Error: Tool '{name}' not found."
        return tool.execute(**kwargs)
