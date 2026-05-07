"""Tool registry."""

from typing import Dict

from core.tools.base import Tool


class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, Tool] = {}

    def register(self, tool: Tool):
        self.tools[tool.name] = tool

    def get(self, name: str) -> Tool:
        if name not in self.tools:
            raise KeyError("Unknown tool: {0}".format(name))
        return self.tools[name]

    def list(self):
        return list(self.tools.values())

