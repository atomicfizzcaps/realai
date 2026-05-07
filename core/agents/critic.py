"""Critic agent."""

from core.agents.base import Agent, AgentContext
from core.inference.registry import InferenceRegistry


class CriticAgent(Agent):
    name = "critic"

    def __init__(self, inference: InferenceRegistry):
        self.inference = inference

    def step(self, messages, context):
        backend = self.inference.get_chat(context["model"])
        critique = backend.generate([
            {"role": "system", "content": "You are a critic. Evaluate the result quality and gaps."},
            *[message.dict() if hasattr(message, "dict") else message for message in messages],
            {"role": "user", "content": "Critique the latest result in one short paragraph."},
        ])
        return {"critique": critique["choices"][0]["message"].get("content", "")}

