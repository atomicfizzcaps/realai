"""Tool registry."""

from typing import Any, Dict

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

    def execute_tool(self, name: str, args: Dict[str, Any], context: Dict[str, Any] = None):
        tool = self.get(name)
        runtime_context = context if isinstance(context, dict) else {}
        required = list(getattr(tool, "permissions", []) or [])
        if runtime_context:
            allowed = set(runtime_context.get("allowed_permissions", []))
            for permission in required:
                if permission not in allowed:
                    raise PermissionError("Permission denied: {0}".format(permission))
        return tool(**(args or {}), _context=runtime_context)
