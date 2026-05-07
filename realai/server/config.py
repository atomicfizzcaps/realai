"""Configuration helpers for the structured RealAI server."""

from dataclasses import dataclass, field
from functools import lru_cache
import copy
import json
from pathlib import Path
from typing import Any, Dict, List

try:
    import tomllib
except ImportError:  # pragma: no cover
    tomllib = None

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

_ROOT = Path(__file__).resolve().parents[2]
_SERVER_ROOT = Path(__file__).resolve().parent
_DEFAULT_REGISTRY_PATH = _ROOT / 'models' / 'registry.json'


@dataclass
class ServerSettings:
    """Typed configuration for the provider-grade server runtime."""

    profile: str = 'default'
    provider: str = 'local'
    default_chat_model: str = 'realai-1.0'
    default_embedding_model: str = 'realai-embed'
    enable_legacy_paths: bool = True
    model_registry_path: str = str(_DEFAULT_REGISTRY_PATH)
    providers: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    profiles: Dict[str, Dict[str, Any]] = field(default_factory=dict)


def _load_toml_file(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    if tomllib is None:
        raise ValueError('tomllib is unavailable; cannot parse {0}'.format(path))
    with path.open('rb') as handle:
        data = tomllib.load(handle)
    return data if isinstance(data, dict) else {}


def _load_yaml_file(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    if yaml is not None:
        with path.open('r', encoding='utf-8') as handle:
            data = yaml.safe_load(handle) or {}
        return data if isinstance(data, dict) else {}
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception as exc:
        raise ValueError('PyYAML is required to parse {0}: {1}'.format(path, exc))


def _profiles_dir() -> Path:
    return _SERVER_ROOT / 'profiles'


def _read_profiles() -> Dict[str, Dict[str, Any]]:
    profiles: Dict[str, Dict[str, Any]] = {}
    root = _profiles_dir()
    if not root.exists():
        return profiles
    for path in sorted(root.glob('*.json')):
        try:
            payload = json.loads(path.read_text(encoding='utf-8'))
        except Exception as exc:
            raise ValueError('Invalid profile file {0}: {1}'.format(path, exc))
        if not isinstance(payload, dict):
            raise ValueError('Profile file {0} must contain an object.'.format(path))
        profile_name = path.stem
        profiles[profile_name] = payload
    return profiles


def _resolve_registry_path(raw_path: str) -> Path:
    path = Path(raw_path)
    if not path.is_absolute():
        path = (_ROOT / path).resolve()
    return path


@lru_cache()
def load_settings() -> ServerSettings:
    """Load typed settings from `realai.toml`, models/providers yaml, and profiles."""
    base = _load_toml_file(_ROOT / 'realai.toml')
    server = base.get('server', {}) if isinstance(base.get('server', {}), dict) else {}
    settings = ServerSettings(
        profile=str(server.get('profile', 'default')),
        provider=str(server.get('provider', 'local')),
        default_chat_model=str(server.get('default_chat_model', 'realai-1.0')),
        default_embedding_model=str(server.get('default_embedding_model', 'realai-embed')),
        enable_legacy_paths=bool(server.get('enable_legacy_paths', True)),
        model_registry_path=str(server.get('model_registry_path', str(_DEFAULT_REGISTRY_PATH))),
    )
    settings.profiles = _read_profiles()
    settings.providers = _load_yaml_file(_ROOT / 'providers.yaml')
    _validate_settings(settings)
    return settings


def _validate_settings(settings: ServerSettings) -> None:
    if not settings.default_chat_model:
        raise ValueError('server.default_chat_model is required.')
    if not settings.default_embedding_model:
        raise ValueError('server.default_embedding_model is required.')
    providers = settings.providers.get('providers', settings.providers)
    if providers and not isinstance(providers, dict):
        raise ValueError('providers.yaml must define an object of providers.')


@lru_cache()
def load_registry() -> Dict[str, Dict[str, Any]]:
    """Load model registry from models.yaml (preferred) or registry.json fallback."""
    settings = load_settings()
    registry_path = _resolve_registry_path(settings.model_registry_path)
    if registry_path.exists():
        data = json.loads(registry_path.read_text(encoding='utf-8'))
    else:
        data = _load_yaml_file(_ROOT / 'models.yaml')
        if not data:
            data = json.loads(_DEFAULT_REGISTRY_PATH.read_text(encoding='utf-8'))
    if not isinstance(data, dict):
        raise ValueError('Model registry must be a JSON/YAML object keyed by model id.')
    return data


def get_model_config(name: str) -> Dict[str, Any]:
    """Return the configuration for a registered model."""
    registry = load_registry()
    if name not in registry:
        raise ValueError('Unknown model {0}'.format(name))
    config = copy.deepcopy(registry[name])
    config.setdefault('id', name)
    return config


def list_models() -> List[str]:
    """List all registered models."""
    return sorted(load_registry().keys())


def list_model_objects() -> List[Dict[str, Any]]:
    """Return provider-style model objects for `/v1/models` responses."""
    data = []
    for model_id in list_models():
        cfg = get_model_config(model_id)
        data.append({
            'id': model_id,
            'object': 'model',
            'owned_by': cfg.get('owned_by', 'realai'),
            'type': cfg.get('type', 'chat'),
            'backend': cfg.get('backend', 'unknown'),
            'context_length': cfg.get('context_length'),
            'embedding_dimensions': cfg.get('embedding_dimensions'),
            'capabilities': cfg.get('capabilities', []),
        })
    return data
