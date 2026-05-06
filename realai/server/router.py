"""Routing helpers for the structured RealAI server."""

from typing import Any, Dict, Iterable, List, Tuple

from .config import get_model_config, list_models
from .embeddings import embed
from .metrics import render_prometheus_text
from .inference import chat_completion


class RequestValidationError(Exception):
    """Raised when a request body is invalid."""

    def __init__(self, message, status_code=400):
        super(RequestValidationError, self).__init__(message)
        self.status_code = status_code


def _require_dict(payload):
    if not isinstance(payload, dict):
        raise RequestValidationError('Request body must be a JSON object.')
    return payload


def _require_messages(messages):
    if not isinstance(messages, list) or not messages:
        raise RequestValidationError('messages must be a non-empty list.')
    for item in messages:
        if not isinstance(item, dict) or 'role' not in item or 'content' not in item:
            raise RequestValidationError('Each message must include role and content.')
    return messages


def _require_input_texts(values):
    if isinstance(values, str):
        return [values]
    if not isinstance(values, list) or not values:
        raise RequestValidationError('input must be a non-empty string or list of strings.')
    for value in values:
        if not isinstance(value, str):
            raise RequestValidationError('All embedding inputs must be strings.')
    return values


def health_response():
    """Return a health payload for the structured server."""
    models = list_models()
    return {
        'status': 'healthy',
        'service': 'RealAI',
        'available_models': models,
        'model_count': len(models),
    }


def handle_chat_request(payload):
    """Handle a chat completions request."""
    payload = _require_dict(payload)
    model_name = payload.get('model')
    if not model_name:
        raise RequestValidationError('model is required.')
    messages = _require_messages(payload.get('messages'))
    config = get_model_config(model_name)
    return chat_completion(
        config,
        messages,
        temperature=payload.get('temperature', 0.2),
        max_tokens=payload.get('max_tokens', 1024),
    )


def handle_embeddings_request(payload):
    """Handle an embeddings request."""
    payload = _require_dict(payload)
    model_name = payload.get('model')
    if not model_name:
        raise RequestValidationError('model is required.')
    inputs = _require_input_texts(payload.get('input'))
    config = get_model_config(model_name)
    vectors = embed(config, inputs)
    return {
        'object': 'list',
        'model': model_name,
        'data': [
            {
                'object': 'embedding',
                'index': index,
                'embedding': vector,
            }
            for index, vector in enumerate(vectors)
        ],
    }


def dispatch_request(method, path, payload=None):
    """Dispatch a request to the structured server router.

    Returns:
        Tuple[int, Any, str]: HTTP status, payload, and content type.
    """
    try:
        if method == 'GET' and path == '/health':
            return 200, health_response(), 'application/json'
        if method == 'GET' and path == '/metrics':
            return 200, render_prometheus_text(), 'text/plain; version=0.0.4'
        if method == 'POST' and path == '/v1/chat/completions':
            return 200, handle_chat_request(payload or {}), 'application/json'
        if method == 'POST' and path == '/v1/embeddings':
            return 200, handle_embeddings_request(payload or {}), 'application/json'
        return 404, {'error': {'message': 'Not found'}}, 'application/json'
    except RequestValidationError as exc:
        return exc.status_code, {'error': {'message': str(exc)}}, 'application/json'
    except KeyError as exc:
        return 404, {'error': {'message': str(exc)}}, 'application/json'
    except Exception as exc:
        return 500, {'error': {'message': str(exc)}}, 'application/json'
