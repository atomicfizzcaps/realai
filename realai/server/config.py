"""Configuration helpers for the structured RealAI server."""

from functools import lru_cache
import copy
import json
from pathlib import Path


@lru_cache()
def load_registry():
    """Load the model registry from disk."""
    path = Path(__file__).resolve().parents[1] / 'models' / 'registry.json'
    return json.loads(path.read_text(encoding='utf-8'))


def get_model_config(name):
    """Return the configuration for a registered model."""
    registry = load_registry()
    if name not in registry:
        raise ValueError('Unknown model {0}'.format(name))
    config = copy.deepcopy(registry[name])
    config.setdefault('id', name)
    return config


def list_models():
    """List all registered models."""
    return sorted(load_registry().keys())
