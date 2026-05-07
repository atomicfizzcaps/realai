"""Synthesizer agent."""

from core.agents.base import Agent, AgentContext
from core.inference.registry import InferenceRegistry


class SynthesizerAgent(Agent):
    name = "synthesizer"

    def __init__(self, inference: InferenceRegistry):
        self.inference = inference

    def step(self, messages, context):
        backend = self.inference.get_chat(context["model"])
        final = backend.generate([
            {"role": "system", "content": "Synthesize all results into a final answer."},
            *[message.dict() if hasattr(message, "dict") else message for message in messages],
            {"role": "user", "content": "Return concise final output with actions taken."},
        ])
        return {"final": final["choices"][0]["message"].get("content", "")}

