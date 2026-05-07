from typing import Any, Dict, List, Protocol

from core.api.schemas.chat import ChatMessage


class AgentContext(Dict[str, Any]):
    ...


class Agent(Protocol):
    name: str

    def step(
        self,
        messages: List[ChatMessage],
        context: AgentContext,
    ) -> Dict[str, Any]:
        ...
