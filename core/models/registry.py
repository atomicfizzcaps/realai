"""Model registry backed by models.yaml."""

from pathlib import Path
from typing import Any, Dict, List

from core.config.loader import Config

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


def _coerce_models(raw: Any) -> List[Dict[str, Any]]:
    if isinstance(raw, dict):
        if "models" in raw and isinstance(raw["models"], list):
            return [item for item in raw["models"] if isinstance(item, dict)]
        output = []
        for model_id, cfg in raw.items():
            if isinstance(cfg, dict):
                item = dict(cfg)
                item.setdefault("id", model_id)
                output.append(item)
        return output
    if isinstance(raw, list):
        return [item for item in raw if isinstance(item, dict)]
    return []


class ModelRegistry:
    """Load model metadata from a YAML registry file."""

    def __init__(self, path: str | None = None):
        cfg = Config()
        path = path or cfg.paths.models
        self.path = Path(path)
        if not self.path.exists():
            self.data = {"models": []}
            return
        text = self.path.read_text(encoding="utf-8")
        if yaml is not None:
            parsed = yaml.safe_load(text) or {}
        else:
            from realai.server.config import _parse_simple_yaml  # local fallback parser
            parsed = _parse_simple_yaml(text)
        self.data = parsed if isinstance(parsed, dict) else {"models": []}

    def list_models(self):
        return _coerce_models(self.data)

