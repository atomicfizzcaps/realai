"""Configuration helpers for the structured RealAI server."""

import copy
import json
import os
from pathlib import Path
from typing import Any, Dict

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_REGISTRY_PATH = _PROJECT_ROOT / 'realai' / 'models' / 'registry.json'
_REGISTRY_CACHE = None


def get_registry_path() -> Path:
    """Return the configured model registry path."""
    override = os.environ.get('REALAI_MODEL_REGISTRY_PATH')
    if override:
        return Path(override).expanduser().resolve()
    return _DEFAULT_REGISTRY_PATH


def load_registry(force_reload=False):
    """Load the model registry from disk.

    Args:
        force_reload: When True, bypass the in-memory cache.

    Returns:
        Dict[str, Dict[str, Any]]: Registry keyed by model name.
    """
    global _REGISTRY_CACHE
    if _REGISTRY_CACHE is None or force_reload:
        registry_path = get_registry_path()
        with registry_path.open('r', encoding='utf-8') as handle:
            _REGISTRY_CACHE = json.load(handle)
    return copy.deepcopy(_REGISTRY_CACHE)


def _resolve_model_path(path_value):
    """Resolve a model path relative to the repository root."""
    if not path_value:
        return path_value
    path_obj = Path(path_value)
    if path_obj.is_absolute():
        return str(path_obj)
    return str((_PROJECT_ROOT / path_obj).resolve())


def get_model_config(name):
    """Return the configuration for a registered model.

    Args:
        name: Model identifier.

    Returns:
        Dict[str, Any]: A copy of the model configuration.

    Raises:
        KeyError: If the model is unknown.
    """
    registry = load_registry()
    if name not in registry:
        raise KeyError('Unknown model {0}'.format(name))
    config = copy.deepcopy(registry[name])
    config.setdefault('id', name)
    config['path'] = _resolve_model_path(config.get('path'))
    return config


def list_models():
    """List all registered models."""
    registry = load_registry()
    return sorted(registry.keys())
