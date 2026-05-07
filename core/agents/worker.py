"""Worker agent."""

import json

from core.agents.base import Agent, AgentContext
from core.inference.registry import InferenceRegistry
from core.tools.registry import ToolRegistry


class WorkerAgent(Agent):
    name = "worker"

    def __init__(self, inference: InferenceRegistry, tools: ToolRegistry):
        self.inference = inference
        self.tools = tools

    def step(self, messages, context):
        tool_call = context.get("tool_call")
        if tool_call:
            tool = self.tools.get(tool_call["name"])
            result = tool(**tool_call.get("arguments", {}))
            return {"result": result, "used_tool": tool_call["name"]}

        backend = self.inference.get_chat(context["model"])
        response = backend.generate([message.dict() if hasattr(message, "dict") else message for message in messages])
        tool_call = _extract_tool_call(response)
        if tool_call:
            tool = self.tools.get(tool_call["name"])
            result = tool(**tool_call.get("arguments", {}))
            return {"result": result, "used_tool": tool_call["name"]}
        return {"response": response}


def _extract_tool_call(response):
    choices = response.get("choices", [])
    if not choices:
        return None
    message = choices[0].get("message", {})
    raw = message.get("tool_call")
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str):
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            return None
    return None

