"""Configuration loader for `realai.toml`."""

from pathlib import Path
from typing import Any

try:
    import tomllib
except ImportError:  # pragma: no cover
    tomllib = None

from .types import PathsConfig, ServerConfig


class Config:
    """Load and read RealAI config using dot-notation keys."""

    def __init__(self, path: str = "realai.toml"):
        self.path = Path(path)
        if not self.path.exists():
            self.data = {}
        else:
            if tomllib is None:
                raise ValueError("tomllib is required to parse realai.toml")
            with self.path.open("rb") as handle:
                self.data = tomllib.load(handle)

        server = self.data.get("server", {}) if isinstance(self.data.get("server"), dict) else {}
        paths = self.data.get("paths", {}) if isinstance(self.data.get("paths"), dict) else {}
        self.server = ServerConfig(
            host=str(server.get("host", "0.0.0.0")),
            port=int(server.get("port", 8000)),
        )
        self.paths = PathsConfig(
            models=str(paths.get("models", "models.yaml")),
            providers=str(paths.get("providers", "providers.yaml")),
        )

    def get(self, key: str, default: Any = None):
        parts = key.split(".")
        node: Any = self.data
        for part in parts:
            if not isinstance(node, dict):
                return default
            if part not in node:
                return default
            node = node[part]
        return node

