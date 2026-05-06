"""Inference helpers for the structured RealAI server."""

import logging
import os
from typing import Any, Dict, List, Optional

from realai import RealAI

from .logging import log_event
from .metrics import increment


def _build_model(config):
    """Instantiate a RealAI model from registry config."""
    api_key_env = config.get('api_key_env')
    api_key = os.environ.get(api_key_env) if api_key_env else None
    base_url_env = config.get('base_url_env')
    base_url = os.environ.get(base_url_env) if base_url_env else config.get('base_url')
    provider = config.get('provider')
    backend = config.get('backend', 'realai')
    use_local = backend in ('hf', 'local', 'realai')
    if use_local and not provider:
        provider = 'local'
    return RealAI(
        model_name=config.get('model_name', config.get('id', 'realai-2.0')),
        api_key=api_key,
        provider=provider,
        base_url=base_url,
        use_local=use_local,
    )


def chat_completion(config, messages, temperature=0.2, max_tokens=1024):
    """Run a chat completion using a configured model."""
    increment('realai_chat_requests_total')
    try:
        model = _build_model(config)
        response = model.chat_completion(
            messages=messages,
            temperature=temperature if temperature is not None else 0.2,
            max_tokens=max_tokens,
        )
        response.setdefault('model', config.get('id', model.model_name))
        log_event(
            logging.INFO,
            'chat_completion',
            model=response.get('model'),
            message_count=len(messages),
        )
        return response
    except Exception as exc:
        increment('realai_chat_failures_total')
        log_event(logging.ERROR, 'chat_completion_failed', error=str(exc))
        raise
