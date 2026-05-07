from typing import Any, Dict, Protocol


class Tool(Protocol):
    name: str
    description: str
    params_schema: Dict[str, Any]
    permissions: list[str]

    def __call__(self, **kwargs: Any) -> Any:
        ...

